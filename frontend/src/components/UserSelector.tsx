import { useQuery } from "@tanstack/react-query";
import React, { useContext, useState } from "react";
import { getData } from "../utils/FetchFunctions";
import UserTable from "./UserTable.tsx";
import AuthContext from "../context/AuthContext.jsx";
import Loading from "./Loading.tsx";

interface Props {
	chosenUsers: Number[];
	handleUserChoice: () => void;
}

const UserSelector = ({
	chosenUsers = [],
	handleUserChoice = () => {},
}: Props) => {
	const { authTokens } = useContext(AuthContext);

	const [searchString, setSearchString] = useState("");
	//get chosen user data

	const {
		data: chosenData,
		isLoading: chosenDataLoading,
		isPending: chosenDataPending,
	} = useQuery({
		queryKey: ["chosenData"],
		queryFn: () => getDataFunc(`user/?id__in=${chosenUsers}`),
	});

	// const { data: searchData, isLoading: searchDataLoading } = useQuery({
	// 	queryKey: ["searchData" + searchString],
	// 	queryFn: () => {
	// 		getDataFunc(`user/?id__not_in=${chosenUsers}&search=${searchString}`);
	// 	},
	// 	enabled: searchString !== "",
	// });

	const getDataFunc = async (apiURL) => {
		let response_json = await getData(apiURL, authTokens.access);
		return response_json;
	};

	//search field

	//handle add user button click

	//handle remove user button click

	//chosen user table

	//search user table

	if (chosenDataLoading || chosenDataPending) {
		return <Loading />;
	}

	console.log(chosenData);

	return (
		<>
			<UserTable userData={chosenData["results"]} />
		</>
	);
};

export default UserSelector;
