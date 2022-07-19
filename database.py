import psycopg2
from config import config

# class for database functions
class Database:
    def __init__(self):
        conn = None
        try:
            params = config()
            self.conn = psycopg2.connect(**params)
            print("Connection success")
        
        except (Exception, psycopg2.DatabaseError) as error:
            print('error')
            print(error)

    # insert one agent into database
    def insert_agent(self, data):
        """ insert a new agent into the trace table """
        sql = """
            INSERT INTO agent(
                uuid,
                age_group,
                sex_group,
                vaccine_willingness,
                incubation_time, 
                dwelling_time, 
                recovery_time, 
                prob_contagion, 
                mortality_value, 
                severity_value,
                curr_dwelling,
                curr_incubation,
                curr_recovery,
                curr_asymptomatic,
                isolated,
                isolated_but_inefficient,
                test_chance,
                in_isolation,
                in_distancing,
                in_testing,
                astep,
                tested,
                occupying_bed,
                cumul_private_value,
                cumul_public_value,
                employed,
                tested_traced,
                tracing_delay,
                tracing_counter,
                vaccinated,
                safetymultiplier,
                current_effectiveness,
                vaccination_day,
                vaccine_count,
                dosage_eligible,
                fully_vaccinated,
                variant
            ) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.cur = self.conn.cursor()
            self.cur.executemany(sql, data)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
    
    # insert one model into the database
    def insert_model(self, data):
        """ insert a new model into the experiment table """
        sql = """
            INSERT INTO experiment(
                uuid,
                test_cost,
                alpha_private,
                alpha_public,
                fully_vaccinated_count,
                prop_initial_infected,
                generally_infected,
                cumul_vaccine_count,
                cumul_test_cost,
                total_costs,
                vaccination_chance,
                vaccination_stage,
                vaccine_cost,
                day_vaccination_begin,
                day_vaccination_end,
                effective_period,
                effectiveness,
                distribution_rate,
                vaccine_count,
                vaccinated_count,
                vaccinated_percent,
                vaccine_dosage,
                effectiveness_per_dosage,
                dwell_15_day,
                avg_dwell,
                avg_incubation,
                repscaling,
                prob_contagion_base,
                kmob,
                rate_inbound,
                prob_contagion_places,
                prob_asymptomatic,
                avg_recovery,
                testing_rate,
                testing_start,
                testing_end,
                tracing_start,
                tracing_end,
                tracing_now,
                isolation_rate,
                isolation_start,
                isolation_end,
                after_isolation,
                prob_isolation_effective,
                distancing,
                distancing_start,
                distancing_end,
                new_agent_num,
                new_agent_start,
                new_agent_end,
                new_agent_age_mean,
                new_agent_prop_infected,
                vaccination_start,
                vaccination_end,
                vaccination_now,
                prob_severe,
                max_bed_available,
                bed_count
            ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        try:
           self.cur = self.conn.cursor()
           self.cur.executemany(sql, data)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    # insert one summary into the database
    def insert_summary(self, data):
        """ insert a new summary into the summary table """
        sql = """
            INSERT INTO summary(
                uuid,
                cumul_priv_value,
                cumul_publ_value,
                cumul_test_cost,
                rt,
                employed,
                unemployed,
                tested,
                traced,
                cumul_vaccine_cost,
                cumul_cost,
                step,
                n,
                isolated,
                vaccinated,
                vaccines,
                v,
                data_time,
                step_time,
                generally_infected,
                fully_vaccinated,
                vaccine_1,
                vaccine_2,
                vaccine_willing
            ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """
        try:
            self.cur = self.conn.cursor()
            self.cur.executemany(sql, data)
        except (Exception, psycopg2.DatabaseError) as error:
            print('error')
            print(error)

    # commit changes to database
    def commit(self):
        self.conn.commit()
    
    # close connection to database
    def close(self):
        if self.cur is not None:
            self.cur.close()
        if self.conn is not None:
            self.conn.close()