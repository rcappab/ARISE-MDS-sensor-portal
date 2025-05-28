import React from "react";
import { useContext, useCallback } from "react";
import AuthContext from "../context/AuthContext";
import { useGoogleReCaptcha } from "react-google-recaptcha-v3";
import { Link } from "react-router-dom";
import CaptchaText from "../components/General/CaptchaText.tsx";

const LoginPage = () => {
	const { loginUser } = useContext(AuthContext);
	const { executeRecaptcha } = useGoogleReCaptcha();

	const handleReCaptchaVerify = useCallback(async () => {
		if (!executeRecaptcha) {
			console.log("Execute recaptcha not yet available");
			return null;
		}

		try {
			const captchaToken = await executeRecaptcha("login");
			return captchaToken;
		} catch (error) {
			console.error("ReCaptcha verification failed:", error);
			return null;
		}
	}, [executeRecaptcha]);

	const handleSubmission = useCallback(
		async (e) => {
			e.preventDefault();

			const captchaToken = await handleReCaptchaVerify();

			const username = e.target.username.value;
			const password = e.target.password.value;

			if (captchaToken) {
				loginUser(username, password, captchaToken);
			} else {
				console.log("Captcha token not set yet");
			}
		},
		[handleReCaptchaVerify, loginUser]
	);

	return (
		<div className="d-flex justify-content-center align-items-center">
			<div className="w-50">
				<h3 className="text-center mb-4">Log In</h3>
				<form onSubmit={handleSubmission}>
					<div className="mb-3">
						<label
							htmlFor="username"
							className="form-label"
						>
							Username
						</label>
						<input
							type="text"
							name="username"
							id="username"
							placeholder="Enter your username"
							className="form-control"
							required
						/>
					</div>
					<div className="mb-3">
						<label
							htmlFor="password"
							className="form-label"
						>
							Password
						</label>
						<input
							type="password"
							name="password"
							id="password"
							placeholder="Enter your password"
							className="form-control"
							required
						/>
					</div>
					<button
						type="submit"
						className="btn btn-primary w-100"
					>
						Log In
					</button>
				</form>
				<div className="mt-3">
					Forgot your password? <Link to={"/reset-password"}>Click here</Link>
					<div className="mt-3">
						Don't have an account? <Link to={"/register"}>Register here</Link>
					</div>
				</div>
				<CaptchaText />
			</div>
		</div>
	);
};

export default LoginPage;
