<script lang="ts">
	import { onMount, onDestroy } from 'svelte';

	let position = $state(0);
	let speed = $state(3);
	let gameOver = $state(false);
	let won = $state(false);
	let message = $state('');
	let inputText = $state('');
	let personName = $state('');
	let personImage = $state('');
	let hints = $state<string[]>([]);
	let revealed = $state(false);
	let interval: ReturnType<typeof setInterval>;

	// reveal hints progressively: 1st at 40%, then every ~12% after
	const hintThresholds = [40, 52, 64, 76, 88];
	const visibleHints = $derived(hints.filter((_, i) => position >= hintThresholds[i]));

	async function fetchPosition() {
		const res = await fetch('http://localhost:8000/position');
		const data = await res.json();
		position = data.position;
		speed = data.speed;
		gameOver = data.game_over;
		won = data.won;
		if (gameOver || won) clearInterval(interval);
	}

	async function interact() {
		const text = inputText.trim();
		if (!text) return;
		inputText = '';
		const res = await fetch('http://localhost:8000/interact', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ text })
		});
		const data = await res.json();
		message = data.message;
		position = data.position;
		speed = data.speed;
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') interact();
	}

	onMount(async () => {
		const [, personRes] = await Promise.all([
			fetch('http://localhost:8000/reset', { method: 'POST' }),
			fetch('http://localhost:8000/person')
		]);
		const person = await personRes.json();
		personName = person.name;
		personImage = person.image;
		hints = person.hints;
		interval = setInterval(fetchPosition, 500);
	});

	onDestroy(() => clearInterval(interval));

	const cliffX = 85;
	const characterX = $derived(Math.min((position / 100) * cliffX, cliffX));
</script>

<div class="game">
	<div class="scene">
		<div class="sky"></div>
		<div class="ground-row">
			<div class="ground"></div>
			<div class="cliff-edge"></div>
			<div class="void"></div>
		</div>

		<div class="character" style="left: {characterX}%; bottom: {gameOver ? -8 : 10}%">
			{gameOver ? '💀' : won ? '🎉' : '🚶'}
		</div>

		<div class="hud">
			<span>position: {position.toFixed(1)}%</span>
			<span>speed: {speed.toFixed(1)}</span>
		</div>

		{#if visibleHints.length > 0}
			<div class="hints">
				{#each visibleHints as hint}
					<span class="hint">{hint}</span>
				{/each}
			</div>
		{/if}
	</div>

	{#if gameOver}
		<div class="overlay">
			{#if revealed}
				<img src={personImage} alt={personName} class="person-photo" />
				<p>You killed {personName}.</p>
			{:else}
				<p>They fell. 💀</p>
				<button onclick={() => (revealed = true)}>Reveal who it was</button>
			{/if}
			<button onclick={() => location.reload()}>Try Again</button>
		</div>
	{:else if won}
		<div class="overlay">
			{#if revealed}
				<img src={personImage} alt={personName} class="person-photo" />
				<p>You saved {personName}!</p>
			{:else}
				<p>You saved them! 🎉</p>
				<button onclick={() => (revealed = true)}>Reveal who it was</button>
			{/if}
			<button onclick={() => location.reload()}>Play Again</button>
		</div>
	{:else}
		<div class="controls">
			{#if message}
				<p class="message">{message}</p>
			{/if}
			<div class="input-row">
				<input
					type="text"
					placeholder="Say something to slow them down..."
					bind:value={inputText}
					onkeydown={onKeydown}
				/>
				<button onclick={interact}>Send</button>
			</div>
		</div>
	{/if}
</div>

<style>
	:global(body) {
		margin: 0;
		background: #111;
		color: #eee;
		font-family: monospace;
	}

	.game {
		display: flex;
		flex-direction: column;
		height: 100vh;
		max-width: 800px;
		margin: 0 auto;
	}

	.scene {
		position: relative;
		flex: 1;
		overflow: hidden;
	}

	.sky {
		position: absolute;
		inset: 0;
		background: linear-gradient(to bottom, #1a1a2e, #16213e);
	}

	.ground-row {
		position: absolute;
		bottom: 0;
		left: 0;
		right: 0;
		height: 10%;
		display: flex;
	}

	.ground {
		flex: 0 0 85%;
		background: #3a5a2a;
		border-top: 3px solid #4a7a3a;
	}

	.cliff-edge {
		flex: 0 0 3%;
		background: linear-gradient(to right, #3a5a2a, #5a3a1a);
		border-top: 3px solid #6a4a2a;
	}

	.void {
		flex: 1;
		background: transparent;
	}

	.character {
		position: absolute;
		font-size: 2rem;
		transition:
			left 0.5s linear,
			bottom 0.3s ease;
		transform: translateX(-50%);
	}

	.hud {
		position: absolute;
		top: 1rem;
		left: 1rem;
		display: flex;
		gap: 1.5rem;
		font-size: 0.8rem;
		opacity: 0.6;
	}

	.hints {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		display: flex;
		gap: 0.75rem;
		background: rgba(0, 0, 0, 0.5);
		padding: 0.5rem 1rem;
		border-radius: 8px;
	}

	.hint {
		font-size: 2rem;
		animation: pop 0.3s ease;
	}

	@keyframes pop {
		from { transform: scale(0); opacity: 0; }
		to   { transform: scale(1); opacity: 1; }
	}

	.overlay {
		padding: 2rem;
		text-align: center;
		font-size: 1.5rem;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
	}

	.person-photo {
		width: 160px;
		height: 160px;
		object-fit: cover;
		border-radius: 50%;
		border: 3px solid #555;
	}

	.overlay p {
		margin: 0;
	}

	.overlay button {
		padding: 0.5rem 1.5rem;
		font-family: monospace;
		cursor: pointer;
	}

	.controls {
		padding: 1rem;
		border-top: 1px solid #333;
	}

	.message {
		margin: 0 0 0.5rem;
		font-size: 0.9rem;
		opacity: 0.8;
	}

	.input-row {
		display: flex;
		gap: 0.5rem;
	}

	input {
		flex: 1;
		padding: 0.5rem;
		background: #222;
		border: 1px solid #444;
		color: #eee;
		font-family: monospace;
		font-size: 1rem;
	}

	button {
		padding: 0.5rem 1rem;
		background: #333;
		border: 1px solid #555;
		color: #eee;
		font-family: monospace;
		cursor: pointer;
	}

	button:hover {
		background: #444;
	}
</style>
