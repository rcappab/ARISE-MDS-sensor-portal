import { createContext, useState } from "react";
import { jwtDecode } from "jwt-decode";
import { Outlet, useNavigate } from "react-router-dom";
import Header from "../pages/Header";
import { useMutation, useQuery } from "@tanstack/react-query";
import toast from "react-hot-toast";

const AuthContext = createContext();

export default AuthContext;

export const AuthProvider = () => {
	const startLoadingToast = () => {
		const toastId = toast.loading("Loading...");
		return toastId;
	};

	const [user, setUser] = useState(() =>
		localStorage.getItem("authTokens")
			? jwtDecode(localStorage.getItem("authTokens"))
			: null
	);
	const [authTokens, setAuthTokens] = useState(() =>
		localStorage.getItem("authTokens")
			? JSON.parse(localStorage.getItem("authTokens"))
			: null
	);

	const navigate = useNavigate();

	const loginUserFunction = async (username, password, recaptchaToken) => {
		let toastId = startLoadingToast();
		const response = await fetch(
			`/${process.env.REACT_APP_API_BASE_URL}/token/`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					username: username,
					password: password,
					recaptcha: recaptchaToken,
				}),
			}
		);
		let data = await response.json();
		if (response.ok) {
			toast.success("Logged in", {
				id: toastId,
			});
			localStorage.setItem("authTokens", JSON.stringify(data));
			setAuthTokens(data);
			setUser(jwtDecode(data.access));
			navigate("/");
		} else {
			toast.error(
				`Error logging in${data["detail"] ? ": " + data["detail"] : ""}`,
				{
					id: toastId,
				}
			);
		}
		return data;
	};

	const doLogIn = useMutation({
		mutationFn: ({ username, password, recaptcha }) =>
			loginUserFunction(username, password, recaptcha),
	});

	let loginUser = async (username, password, recaptchaToken) => {
		doLogIn.mutate({
			username: username,
			password: password,
			recaptcha: recaptchaToken,
		});
	};

	const updateToken = async () => {
		const response = await fetch(
			`/${process.env.REACT_APP_API_BASE_URL}/token/refresh/`,
			{
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ refresh: authTokens?.refresh }),
			}
		);

		const data = await response.json();
		if (response.status === 200) {
			setAuthTokens(data);
			setUser(jwtDecode(data.access));
			localStorage.setItem("authTokens", JSON.stringify(data));
		} else {
			logoutUser();
		}
		return data;
	};

	useQuery({
		queryKey: [`refreshToken-${user}`],
		queryFn: updateToken,
		enabled: authTokens != null,
		refetchInterval: 1000 * 60 * 4,
		refetchOnWindowFocus: true,
	});

	let logoutUser = (e) => {
		if (e) {
			e.preventDefault();
		}
		localStorage.removeItem("authTokens");
		setAuthTokens(null);
		setUser(null);
		navigate("/login");
	};

	let contextData = {
		user: user,
		authTokens: authTokens,
		loginUser: loginUser,
		logoutUser: logoutUser,
	};

	// useEffect(()=>{

	//     const REFRESH_INTERVAL = 1000 * 60 * 4 // 4 minutes
	//     let interval = setInterval(()=>{
	//         if(authTokens){
	//             updateToken()
	//         }
	//     }, REFRESH_INTERVAL)
	//     return () => clearInterval(interval)

	// },[authTokens, loading])

	return (
		<AuthContext.Provider value={contextData}>
			<Header />
			<div className="container pt-3">
				<Outlet />
			</div>
		</AuthContext.Provider>
	);
};
