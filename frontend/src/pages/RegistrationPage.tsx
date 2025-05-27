import { useMutation } from "@tanstack/react-query";
import React from "react";
import { useState, useCallback, useEffect } from "react";
import { useGoogleReCaptcha } from "react-google-recaptcha-v3";
import toast from "react-hot-toast";
import { useNavigate } from "react-router-dom";
import CaptchaText from "../components/General/CaptchaText.tsx";

const RegistraionPage = () => {
	const [CaptchaToken, setCaptchaToken] = useState<string | null>(null);
	const { executeRecaptcha } = useGoogleReCaptcha();
	const navigate = useNavigate();

	// Create an event handler so you can call the verification on button click event or form submit
	const handleReCaptchaVerify = useCallback(async () => {
		if (!executeRecaptcha) {
			console.log("Execute recaptcha not yet available");
			return;
		}

		await executeRecaptcha("register")
			.then((result) => {
				setCaptchaToken(result);
			})
			.catch((error) => {
				console.error("Promise rejected with:", error);
			});
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
		e.preventDefault();
		handleReCaptchaVerify();
		let toastId = startLoadingToast();
		let response;

		if (CaptchaToken) {
			const formData = new FormData(e.target);
			const data = {
				username: formData.get("username"),
				email: formData.get("email"),
				password: formData.get("password"),
				confirm_password: formData.get("confirm_password"),
				first_name: formData.get("first_name"),
				last_name: formData.get("last_name"),
				organisation: formData.get("organisation"),
				bio: formData.get("bio"),
				recaptcha: CaptchaToken,
			};
			response = await doPost.mutateAsync({
				apiURL: `user/`,
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
				doPost.reset();
			} else {
				toast.success(response["detail"], {
					id: toastId,
				});
				navigate("/login");
			}
		} else {
			console.log("Captcha token not set yet");
		}
	};

	return (
		<>
			<div className="d-flex justify-content-center align-items-center">
				<div className="w-50 m-3">
					<h2 className="text-center mb-4">User Registration</h2>
					<form onSubmit={handleSubmission}>
						<div className="mb-3">
							<label
								htmlFor="email"
								className="form-label"
							>
								Email
							</label>
							<input
								type="email"
								name="email"
								id="email"
								placeholder="Enter email"
								className="form-control"
								required
							/>
						</div>
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
								placeholder="Enter username"
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
								placeholder="Enter password"
								className="form-control"
								required
							/>
						</div>
						<div className="mb-3">
							<label
								htmlFor="confirm_password"
								className="form-label"
							>
								Confirm Password
							</label>
							<input
								type="password"
								name="confirm_password"
								id="confirm_password"
								placeholder="Confirm password"
								className="form-control"
								required
							/>
						</div>
						<div className="row mb-3">
							<div className="col">
								<label
									htmlFor="first_name"
									className="form-label"
								>
									First Name
								</label>
								<input
									type="text"
									name="first_name"
									id="first_name"
									placeholder="First name"
									className="form-control"
									required
								/>
							</div>
							<div className="col">
								<label
									htmlFor="last_name"
									className="form-label"
								>
									Last Name
								</label>
								<input
									type="text"
									name="last_name"
									id="last_name"
									placeholder="Last name"
									className="form-control"
									required
								/>
							</div>
						</div>
						<div className="mb-3">
							<label
								htmlFor="organisation"
								className="form-label"
							>
								Organisation
							</label>
							<input
								type="text"
								name="organisation"
								id="organisation"
								placeholder="Organisation name"
								className="form-control"
							/>
						</div>
						<div className="mb-3">
							<label
								htmlFor="bio"
								className="form-label"
							>
								Reason for Registration
							</label>
							<textarea
								name="bio"
								id="bio"
								placeholder="Reason for registration"
								className="form-control"
								rows={4}
							></textarea>
						</div>
						<button
							type="submit"
							className="btn btn-primary w-100"
						>
							Register
						</button>
					</form>
				</div>
			</div>
			<div>
				<p>Privacy Statement</p>
				We collect and store the following personal data to manage access to
				research data: first name, last name, email address, username, and a
				hashed password. This information is securely stored on servers located
				within the faculty and is retained only for as long as access management
				is required. Access to this data is restricted to authorized personnel
				and handled in accordance with applicable data protection regulations,
				including account closure requests. To request an account closure ,
				please send an e-mail from the e-mail address you signed up with to this
				e-mail address.
			</div>
			<CaptchaText />
		</>
	);
};

export default RegistraionPage;
