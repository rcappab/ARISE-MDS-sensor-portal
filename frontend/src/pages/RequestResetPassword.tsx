import React, { useCallback, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useGoogleReCaptcha } from "react-google-recaptcha-v3";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";

const RequestResetPassword = () => {
	const [CaptchaToken, setCaptchaToken] = useState(null);
	const { executeRecaptcha } = useGoogleReCaptcha();
	const navigate = useNavigate();

	// Create an event handler so you can call the verification on button click event or form submit
	const handleReCaptchaVerify = useCallback(async () => {
		if (!executeRecaptcha) {
			console.log("Execute recaptcha not yet available");
			return;
		}

		const token = await executeRecaptcha("resetpassword");
		setCaptchaToken(token);
		//verifyCaptcha(token);
		// Do whatever you want with the token
	}, [executeRecaptcha, setCaptchaToken]);

	const postData = async function (url, data) {
		let response = await fetch(
			`/${process.env.REACT_APP_API_BASE_URL}/${url}`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(data),
			}
		);
		let response_json = await response.json();
		response_json["ok"] = response.ok;
		response_json["statusText"] = response.statusText;
		// if (!response.ok) {
		// 	throw new Error(response.statusText);
		// }
		return response_json;
	};

	const newPOST = async function (x: { apiURL: string; data: object }) {
		let response_json = await postData(x.apiURL, x.data);
		return response_json;
	};

	const doPost = useMutation({
		mutationFn: (inputValue: { apiURL: string; data: object }) =>
			newPOST(inputValue),
	});

	const startLoadingToast = () => {
		const toastId = toast.loading("Loading...");
		return toastId;
	};

	useEffect(() => {
		handleReCaptchaVerify();
	}, [handleReCaptchaVerify]);

	const handleSubmission = async function (e) {
		// POST EMAIL TO API
		e.preventDefault();
		handleReCaptchaVerify();
		let toastId = startLoadingToast();
		let response;

		if (CaptchaToken) {
			const data = {
				email: email,
			};
			console.log(data);
			response = await doPost.mutateAsync({
				apiURL: `password_reset/`,
				data: data,
			});
			if (!response["ok"]) {
				toast.error(
					`Error in submission ${
						response["detail"] ? ":" + response["detail"] : ""
					}`,
					{
						id: toastId,
					}
				);
			} else {
				console.log(response);
				toast.success("Password reset succesfully requested", {
					id: toastId,
				});
				navigate("success");
			}
		} else {
			console.log("Captcha token not set yet");
		}
	};

	const [email, setEmail] = useState("");
	return (
		<div className="d-flex justify-content-center align-items-center">
			<div className="w-50">
				<h3 className="text-center mb-4">Reset Password</h3>
				<p>Enter your email to reset your password.</p>

				<div>
					<input
						type="email"
						className="form-control mb-3"
						placeholder="Enter your email"
						value={email}
						onChange={(e) => setEmail(e.target.value)}
					/>
				</div>
				<div className="text-center mb-3">
					<button
						type="button"
						className="btn btn-primary"
						onClick={handleSubmission}
						disabled={email.length === 0 || !doPost.isIdle}
					>
						Send Reset Link
					</button>
				</div>
			</div>
		</div>
	);
};

export default RequestResetPassword;
