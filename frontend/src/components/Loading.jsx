import React from "react";
import "../styles/loading.css";
const Loading = () => {
	return (
		<div
			id="loading-div"
			className="text-center loading-div"
		>
			<div
				className="spinner-border"
				role="status"
			></div>
			<span className="spinner-text">Loading...</span>
		</div>
	);
};

export default Loading;
