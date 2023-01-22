<script lang="ts">
	export let currentView;

	function click(step) {
		currentView = step;
	}
</script>

<div class="stepper-wrapper">
	<div class="stepper-item completed" id="stepper-1" on:click={() => click(1)}>
		<div class="step-counter">1</div>
		<div class="step-name">Ensemble</div>
	</div>
	<div class="stepper-item" class:completed={currentView >= 2} class:active={currentView < 2} id="stepper-2" on:click={() => click(2)}>
		<div class="step-counter">2</div>
		<div class="step-name">Simulation</div>
	</div>
	<div class="stepper-item" class:completed={currentView >= 3} class:active={currentView < 3} id="stepper-3" on:click={() => click(3)}>
		<div class="step-counter">3</div>
		<div class="step-name">Agent</div>
	</div>
</div>

<style>
    .stepper-wrapper {
        display: flex;
        justify-content: space-between;
        margin: 20px;
    }
    .stepper-item {
        position: relative;
        display: flex;
        flex-direction: column;
        align-items: center;
        flex: 1;
    }

    .stepper-item::before {
        position: absolute;
        content: "";
        border-bottom: 2px solid #ccc;
        width: 100%;
        top: 15px;
        left: -50%;
        z-index: 2;
    }

    .stepper-item::after {
        position: absolute;
        content: "";
        border-bottom: 2px solid #ccc;
        width: 100%;
        top: 15px;
        left: 50%;
        z-index: 2;
    }

    .stepper-item .step-counter {
        position: relative;
        z-index: 5;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        background: #ccc;
        margin-bottom: 6px;
        cursor: pointer;
    }

    .stepper-item.completed {
        font-weight: bold;
    }

    .stepper-item.completed .step-counter {
        background-color: #84b09b;
    }

    .stepper-item.completed::before {
        position: absolute;
        content: "";
        border-bottom: 2px solid #84b09b;
        width: 100%;
        top: 15px;
        left: -50%;
        z-index: 3;
    }

    .stepper-item:first-child::before {
        content: none;
    }
    .stepper-item:last-child::after {
        content: none;
    }
</style>