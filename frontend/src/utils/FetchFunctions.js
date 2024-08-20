// Submit data to API
async function SubmitData(url, data, method = "POST") {
	let response = await fetch(url, {
		method: method,
		headers: {
			"X-CSRFToken": document.head.querySelector("meta[name=csrf-token]")
				.content,
		},
		mode: "same-origin",
		body: data,
	});

	let response_json = await response.json();
	response_json["ok"] = response.ok;
	return response_json;
}

// Get data from API
async function getData(url, token) {
	let response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/${url}`, {
		headers: {
			Authorization: "Bearer " + String(token),
			"Content-Type": "application/json",
		},
	});
	return response;
	// let response_json = await response.json();
	// response_json["ok"] = response.ok;
	// return response_json;
}
export default getData;
