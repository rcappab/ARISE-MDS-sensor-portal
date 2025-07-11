// Get data from API
export async function getData(url, token) {
	let response = await fetch(`/${process.env.REACT_APP_API_BASE_URL}/${url}`, {
		headers: {
			Authorization: "Bearer " + String(token),
			"Content-Type": "application/json",
		},
	});
	return await handleResponse(response);
}

export async function postDataFiles(url, token, data, files) {
	const body = new FormData();
	for (const key in data) {
		body.append(key, data[key]);
	}
	for (const file of files) {
		body.append("files", file, file.name);
	}

	const response_json = await postBody(url, token, body, false);
	return response_json;
}

export async function postData(url, token, data) {
	const body = JSON.stringify(data);
	const response_json = await postBody(url, token, body);
	return response_json;
}

export async function postBody(url, token, body, json = true) {
	const headers = {
		Authorization: "Bearer " + String(token),
	};
	if (json) {
		headers["Content-Type"] = "application/json";
	}
	let response = await fetch(`/${process.env.REACT_APP_API_BASE_URL}/${url}`, {
		method: "POST",
		headers: headers,
		body: body,
	});

	return await handleResponse(response);
}

export async function patchData(url, token, data) {
	let response = await fetch(`/${process.env.REACT_APP_API_BASE_URL}/${url}`, {
		method: "PATCH",
		headers: {
			Authorization: "Bearer " + String(token),
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	});

	return await handleResponse(response);
}

export async function deleteData(url, token) {
	let response = await fetch(`/${process.env.REACT_APP_API_BASE_URL}/${url}`, {
		method: "DELETE",
		headers: {
			Authorization: "Bearer " + String(token),
			"Content-Type": "application/json",
		},
	});

	return await handleResponse(response);
}

async function handleResponse(response) {
	let response_json = { ok: response.ok, statusText: response.statusText };
	try {
		const response_data = await response.json();
		if (Array.isArray(response_data)) {
			response_json.results = response_data;
		} else {
			Object.assign(response_json, response_data);
		}
	} catch (error) {}

	return response_json;
}
