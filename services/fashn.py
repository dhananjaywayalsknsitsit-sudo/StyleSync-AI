import base64, mimetypes, os, time
import requests

BASE = "https://api.fashn.ai"

def as_data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "image/jpeg"
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{encoded}"

def create_tryon(person_path, garment_path, prompt, config):
    api_key = config.get("FASHN_API_KEY")
    if not api_key:
        raise RuntimeError("AI API key missing. Add FASHN_API_KEY to your .env file.")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model_name": "tryon-max",
        "inputs": {
            "product_image": as_data_uri(garment_path),
            "model_image": as_data_uri(person_path),
            "prompt": prompt,
            "resolution": "1k",
            "generation_mode": "balanced",
            "num_images": 1,
            "output_format": "png"
        }
    }
    response = requests.post(f"{BASE}/v1/run", json=payload, headers=headers, timeout=60)
    if not response.ok:
        raise RuntimeError(f"AI provider error ({response.status_code}): {response.text[:400]}")
    data = response.json()
    prediction_id = data.get("id")
    if not prediction_id:
        raise RuntimeError(f"AI provider did not return a prediction ID: {data}")
    for _ in range(60):
        time.sleep(3)
        status_response = requests.get(f"{BASE}/v1/status/{prediction_id}", headers=headers, timeout=30)
        status_response.raise_for_status()
        status_data = status_response.json()
        status = status_data.get("status")
        if status == "completed":
            output = status_data.get("output") or []
            if output:
                return output[0]
            raise RuntimeError("AI completed but returned no output image.")
        if status == "failed":
            error = status_data.get("error") or {}
            raise RuntimeError(error.get("message", "AI image generation failed."))
    raise TimeoutError("AI generation is taking too long. Please try again later.")
