import React from "react";
import { useContext } from "react";
import AuthContext from "../context/AuthContext";

const HomePage = () => {
	const { user } = useContext(AuthContext);

	return user ? (
		<div>
			<title>Home</title>
			This is the home page
		</div>
	) : (
		<div>
			<title>Please log in</title>
			<p>You are not logged in, redirecting...</p>
		</div>
	);
};

export default HomePage;
