import React from "react";
import { useContext } from "react";
import AuthContext from "../context/AuthContext";

const HomePage = () => {
	const { user } = useContext(AuthContext);

	return user ? (
		<div>This is the home page</div>
	) : (
		<div>
			<p>You are not logged in, redirecting...</p>
		</div>
	);
};

export default HomePage;
