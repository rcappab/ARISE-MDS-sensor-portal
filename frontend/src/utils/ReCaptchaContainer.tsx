import React, { useCallback, useEffect } from "react";

import { useGoogleReCaptcha } from "react-google-recaptcha-v3";

interface ReCaptchaContainerProps {
	actionName: string;
}

const ReCaptchaContainer = ({ actionName }: ReCaptchaContainerProps) => {
	const { executeRecaptcha } = useGoogleReCaptcha();

	// const verifyCaptcha = async (token) => {
	// 	const response = await fetch(
	// 		`https://www.google.com/recaptcha/api/siteverify?secret=${secretKey}&response=${token}`,
	// 		{ method: "POST" }
	// 	);

	// 	const data = await response.json();
	// 	console.log("reCAPTCHA verification result:", data);
	// };

	// Create an event handler so you can call the verification on button click event or form submit
	const handleReCaptchaVerify = useCallback(async () => {
		if (!executeRecaptcha) {
			console.log("Execute recaptcha not yet available");
			return;
		}

		const token = await executeRecaptcha(actionName);
		console.log(token);
		//verifyCaptcha(token);
		// Do whatever you want with the token
	}, [executeRecaptcha, actionName]);

	// You can use useEffect to trigger the verification as soon as the component being loaded
	useEffect(() => {
		handleReCaptchaVerify();
	}, [handleReCaptchaVerify]);

	return <button onClick={handleReCaptchaVerify}>Verify recaptcha</button>;
};

export default ReCaptchaContainer;
