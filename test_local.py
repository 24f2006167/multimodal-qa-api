import base64
import requests

url = "http://127.0.0.1:8003/answer-image"

def test_image(image_path, question, expected):
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    payload = {"image_base64": img_b64, "question": question}
    resp = requests.post(url, json=payload, timeout=60)
    result = resp.json()
    got = result.get("answer")

    match = "✅" if str(got).strip() == str(expected).strip() else "❌"
    print(f"{match} {image_path}")
    print(f"   Question: {question}")
    print(f"   Expected: {expected}")
    print(f"   Got:      {got}")
    print()

test_image("test_invoice.png", "What is the invoice grand total including tax?", "495.00")
test_image("test_receipt.png", "What is the grand total on the receipt?", "465.00")
test_image("test_piechart.png", "Which category has the largest share of the budget?", "Housing")