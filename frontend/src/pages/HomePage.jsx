import React from "react";
import { useContext } from "react";
import AuthContext from "../context/AuthContext";
import { getData } from "../utils/FetchFunctions.js";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import Loading from "../components/General/Loading.tsx";
import DeploymentMap from "../components/Maps/DeploymentMap.tsx";

const HomePage = () => {
	const { authTokens, user } = useContext(AuthContext);

	const getDataFunc = async () => {
		let apiURL = `${"deployment"}/?is_active=True`;
		let response_json = await getData(apiURL, authTokens.access);
		if (response_json.hasOwnProperty("results")) {
			return response_json.results;
		}
		return response_json;
	};

	const {
		isLoading,
		//isError,
		isPending,
		data,
		//error,
		isRefetching,
		isPlaceholderData,
		//refetch,
	} = useQuery({
		queryKey: ["deploymentdata", user],
		queryFn: () => getDataFunc(),
		refetchOnWindowFocus: false,
		placeholderData: keepPreviousData,
	});

	if ((isLoading || isPending || isRefetching) & !isPlaceholderData) {
		return <Loading />;
	}
	return <DeploymentMap deployments={data} />;
};

export default HomePage;
