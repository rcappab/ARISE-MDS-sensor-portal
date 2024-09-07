// Get data from API
export async function getData(url, token) {
	let response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/${url}`, {
		headers: {
			Authorization: "Bearer " + String(token),
			"Content-Type": "application/json",
		},
	});
	if (!response.ok) {
		throw new Error(response.statusText);
	}
	return response.json();
}

export async function postData(url, token, data) {
	let response = await fetch(`${process.env.REACT_APP_API_BASE_URL}/${url}`, {
		method: "POST",
		headers: {
			Authorization: "Bearer " + String(token),
			"Content-Type": "application/json",
		},
		body: JSON.stringify(data),
	});
	if (!response.ok) {
		throw new Error(response.statusText);
	}
	return response.json();
}
