import React from "react";
import { Link } from "react-router-dom";

const PostResetPassword = () => {
	return (
		<div className="d-flex justify-content-center align-items-center">
			<div className="w-50">
				<h4 className="mb-3">Reset Password</h4>
				<p>
					An email has been sent to this email address with instructions on how
					to reset your password.
				</p>
				<Link
					to="/login"
					className="btn btn-primary mt-3"
				>
					Back to Login
				</Link>
			</div>
		</div>
	);
};

export default PostResetPassword;
