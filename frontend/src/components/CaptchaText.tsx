import React from "react";

const CaptchaText: React.FC = () => {
	return (
		<div className="mt-3">
			<p className="text-muted fw-light text-center">
				This site is protected by reCAPTCHA and the Google{" "}
				<a href="https://policies.google.com/privacy">Privacy Policy</a> and{" "}
				<a href="https://policies.google.com/terms">Terms of Service</a> apply.
			</p>
		</div>
	);
};

export default CaptchaText;
