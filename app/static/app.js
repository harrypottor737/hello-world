const form = document.getElementById('dub-form');
const result = document.getElementById('result');
const origVideo = document.getElementById('origVideo');
const dubVideo = document.getElementById('dubVideo');
const downloadLink = document.getElementById('downloadLink');

form.addEventListener('submit', async (e) => {
	e.preventDefault();
	const data = new FormData(form);
	const resp = await fetch('/api/dub', { method: 'POST', body: data });
	if (!resp.ok) {
		const err = await resp.text();
		alert('Failed: ' + err);
		return;
	}
	const json = await resp.json();
	origVideo.src = json.originalVideoUrl;
	dubVideo.src = json.dubbedVideoUrl;
	downloadLink.href = json.dubbedVideoUrl;
	result.classList.remove('hidden');
});