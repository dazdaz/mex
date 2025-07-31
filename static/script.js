document.addEventListener('DOMContentLoaded', () => {
    const handleFormSubmit = async (panelId) => {
        const form = document.querySelector(`#${panelId} .panel-form`);
        const responseArea = document.querySelector(`#${panelId} .response-area`);
        const responseCode = responseArea.querySelector('code');
        const submitButton = form.querySelector('button');

        form.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(form);
            const model = formData.get('model');
            const prompt = formData.get('prompt');

            submitButton.setAttribute('aria-busy', 'true');
            submitButton.disabled = true;
            responseCode.textContent = 'Generating response...';

            try {
                const apiResponse = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ model, prompt }),
                });

                const result = await apiResponse.json();
                responseCode.textContent = apiResponse.ok ? result.response : `Error: ${result.error || 'Unknown error'}`;

            } catch (error) {
                responseCode.textContent = `Network or server error: ${error.message}`;
            } finally {
                submitButton.setAttribute('aria-busy', 'false');
                submitButton.disabled = false;
            }
        });
    };

    handleFormSubmit('panel-1');
    handleFormSubmit('panel-2');
});
