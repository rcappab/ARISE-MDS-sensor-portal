import React, { useCallback, useEffect } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useState } from "react";
import { useGoogleReCaptcha } from "react-google-recaptcha-v3";
import { useMutation } from "@tanstack/react-query";
import toast from "react-hot-toast";

const DoResetPassword = () => {
	const [CaptchaToken, setCaptchaToken] = useState<string | null>(null);
	const { executeRecaptcha } = useGoogleReCaptcha();
	const [searchParams] = useSearchParams();
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
				password: password,
				token: searchParams.get("token"),
			};
			response = await doPost.mutateAsync({
				apiURL: `password_reset/confirm/`,
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
				toast.success("Password succesfully changed!", {
					id: toastId,
				});
				navigate("/login");
			}
		} else {
			console.log("Captcha token not set yet");
		}
	};

	const [password, setPassword] = useState("");
	return (
		<div className="d-flex justify-content-center align-items-center">
			<div className="w-50">
				<h3 className="text-center mb-4">Change Password</h3>
				<p>Enter your new password.</p>

				<div>
					<input
						type="password"
						className="form-control mb-3"
						placeholder="Enter new password"
						value={password}
						onChange={(e) => setPassword(e.target.value)}
					/>
				</div>
				<div className="text-center mb-3">
					<button
						type="button"
						className="btn btn-primary"
						onClick={handleSubmission}
						disabled={password.length === 0 || !doPost.isIdle}
					>
						Send Reset Link
					</button>
				</div>
			</div>
		</div>
	);
};

export default DoResetPassword;
