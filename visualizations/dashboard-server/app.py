import redis
import pandas as pd
import numpy as np
import json

from flask import Flask, request, Response,jsonify
from flask_cors import CORS, cross_origin
from werkzeug.utils import secure_filename


app = Flask(__name__)
cors = CORS(app)
r = redis.Redis(host='localhost', port=6379, db=0)
datafilesPrefix = "./data/"
defaultFile, defaultKey = "sims_5_steps_200.csv", "sims_5_steps_200"

app.config['CORS_HEADERS'] = 'Content-Type'

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/check')
def check():
    return str(r.set('key', 'value'))

@app.route('/load', methods=['GET','POST'])
def load():
    if request.method == 'POST':
        f = request.files.get('file')
        filename = secure_filename(f.filename)
        f.save(f"{datafilesPrefix}{filename}")
    file = datafilesPrefix + request.args.get('filename', default=defaultFile, type=str)
    return loadFile(file)

@app.route('/data')
@cross_origin()
def data():
    key = request.args.get('filename', default=defaultKey, type=str)
    field = request.args.get('field', default="agg", type=str)
    return Response(json.dumps(json.loads(r.hget(key, field))),  mimetype='application/json')

@app.route('/data/ensemble')
@cross_origin()
def ensemble():
    key = request.args.get('filename', default=defaultKey, type=str)

    stages = request.args.getlist('stage', type=str)
    stages = [stage for stage in stages if r.hexists(key, stage)]
    if not stages:
        d = {
            "agg": [],
            "maxFreq": 0,
            "maxStep": int(r.hget(key, "maxStep")),
            "details": [],
        }
        return Response(json.dumps(d),  mimetype='application/json')
    
    details = pd.concat([pd.read_json(r.hget(key, stage), orient='split') for stage in stages])\
        [['run','step','count']].groupby(by=['run','step']).sum().reset_index()
    
    agg = details.groupby(['step']).agg({'count': [np.min,np.max,np.mean]})
    agg.columns = agg.columns.get_level_values(1)
    agg = agg.rename({'amin': 'min', 'amax': 'max'}, axis=1).reset_index().to_json(orient="records")

    maxFreq = details['count'].max()
    maxStep = r.hget(key, "maxStep")
    d = {
        "agg": json.loads(agg),
        "maxFreq": int(maxFreq),
        "maxStep": int(maxStep),
        "details": json.loads(details.to_json(orient="records")),
    }

    return Response(json.dumps(d),  mimetype='application/json')


@app.route('/data/simulation')
@cross_origin()
def simulation():
    key = request.args.get('filename', default=defaultKey, type=str)
    id = request.args.get('id', default=0, type=str)
    run = json.loads(r.hget(key, f"run-{id}"))
    return Response(json.dumps(run), mimetype='application/json')

@app.route('/data/states')
@cross_origin()
def states():
    key = request.args.get('filename', default=defaultKey, type=str)
    run = json.loads(r.hget(key, "state-transitions"))
    return Response(json.dumps(run), mimetype='application/json')

@app.route('/files')
def files():
    return jsonify(list(map(lambda s: s.decode("utf-8"), r.keys())))

def loadFile(filename: str):
    print("loading...")
    df = pd.read_csv(filename)
    key = filename.replace(".csv", "").replace("./data/","")
    print("finish loading...")
    print("parsing...")
    parseEnsemble(df, key)
    parseSimulation(df, key)
    parseAgent(df, key)
    return "True"

def parseAgent(df: pd.DataFrame, key: str):
    # print("saving individual agents...")
    # for id in df.id.unique():
    #     data = df[df['id'] == id].to_json(orient='records')
    #     r.hset(key, f"agent-{id}", data)

    print("creating stage transition edges...")
    ag = df.sort_values(['id','run','step']).reset_index()[['run','step','id','stage']]
    ag['prev'] = ag.stage.shift(1)
    ag = ag.query('stage != prev | step == 0')
    ag['start'] = ag.index
    ag['start'] = ag.start.shift(1)
    ag = ag.dropna()
    ag['steps'] = ag.index - ag.start
    ag = ag[ag['step'] != 0]
    ag['stage'] = ag['stage']. str.replace("Stage.", "")
    ag['prev'] = ag['prev'].str.replace("Stage.", "")
    ag['edge'] = ag[['prev','stage']].agg(' → '.join, axis=1)
    r.hset(key, "state-transitions", ag[['step','edge','id','steps']].to_json(orient='records'))

def parseEnsemble(df: pd.DataFrame, key: str):
    r.hset(key, "maxStep", int(df['step'].max()))
    de = df.groupby(['run','step','stage']).count().reset_index().pivot(index='step',columns=['stage', 'run'],values=['id']).fillna(0).unstack().reset_index().drop('level_0', axis=1)
    de = de.rename(columns={0: "count"})

    for stage in de.stage.unique():
        s = de.loc[de.stage == stage][['run','step','count']]        
        r.hset(key, f"{stage}", s.to_json(orient='split'))


    # agg = df[df['stage'].isin(["Stage.SYMPDETECTED", "Stage.SEVERE","Stage.EXPOSED","Stage.ASYMPTOMATIC"])].groupby(['run','step']).count().reset_index()
    # agg['count'] = agg.id
    # agg = agg[['run','step','count']]

    # r.hset(key, "maxFreq", int(agg['count'].max()))
    # r.hset(key, "maxStep", int(agg['step'].max()))

    # r.hset(key, "aggDetails", agg.to_json(orient="records"))

    # print("creating min max for ensemble...")
    # details = agg.sort_values(['step','run']).set_index(['step','run']).groupby(level=0).apply(lambda df: df.xs(df.name).to_dict()).to_dict()
    # minMax = {}
    # for step, runs in details.items():
    #     mins, maxs = [], []
    #     minVal = float('inf')
    #     maxVal = float('-inf')
    #     for run, count in runs['count'].items():
    #         if count < minVal:
    #             minVal = count
    #             mins = []
    #         if count > maxVal:
    #             maxVal = count
    #             maxs = []
    #         if count == minVal:
    #             mins.append(run)
    #         if count == maxVal:
    #             maxs.append(run)
    #     minMax[step] = {"min": mins, "max": maxs}

    # r.hset(key, "minmax", json.dumps(minMax))

    # print("creating agg summary for ensemble...")

    # agg = agg.groupby(['step']).agg({'count': [np.min,np.max,np.mean]})
    # agg.columns = agg.columns.get_level_values(1)
    # agg = agg.rename({'amin': 'min', 'amax': 'max'}, axis=1)
    # agg = agg.reset_index()
    # agg.to_json(orient="records")

    # r.hset(key, "agg", agg.to_json(orient="records", index=True))

def parseSimulation(df: pd.DataFrame, key: str):
    print("saving individual simulations...")
    if (df.run.max() * df.step.max() > 50000): return
    for run in df.run.unique():
        data = df[df['run'] == run].to_json(orient='records')
        r.hset(key, f"run-{run}", data)
