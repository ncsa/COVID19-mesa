<script>
	export let name;
	export let color;
</script>

<style>

	.box {
			display: inline-block;
			float: left;
			width: 20px;
			height: 10px;
			clear: both;
			align-self: center;
	}

  .stage {
      display: flex;
      flex-grow: 1;
			align-content: center;
			gap: 5px;
  }
</style>

<div class='stage'>
	<span class='box' style='background-color: {color}'></span>
	<span>{name}</span>
</div>

