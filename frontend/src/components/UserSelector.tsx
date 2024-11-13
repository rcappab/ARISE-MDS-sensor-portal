import { keepPreviousData, useQuery } from "@tanstack/react-query";
import React, { useContext, useState } from "react";
import { getData } from "../utils/FetchFunctions";
import UserTable from "./UserTable.tsx";
import AuthContext from "../context/AuthContext.jsx";
import Loading from "./Loading.tsx";

interface Props {
	chosenUsers: Number[];
	onPermissionChange: (number, boolean) => void;
}

const UserSelector = ({
	chosenUsers = [],
	onPermissionChange = () => {},
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

	const {
		data: searchData,
		isLoading: searchDataLoading,
		isPending: searchDataPending,
	} = useQuery({
		queryKey: ["searchData_" + searchString],
		queryFn: () =>
			getDataFunc(`user/?id__not_in=${chosenUsers}&search=${searchString}`),
		enabled: searchString !== "",
	});

	const getDataFunc = async (apiURL) => {
		let response_json = await getData(apiURL, authTokens.access);
		return response_json;
	};

	//search field

	//handle remove user button click

	//chosen user table

	//search user table

	return (
		<>
			{chosenDataLoading || chosenDataPending ? (
				<Loading />
			) : (
				<UserTable
					tableID="existing_users"
					userData={chosenData["results"]}
					buttonText="Remove"
					button={true}
					buttonClass="btn btn-danger"
				/>
			)}
			Search users:{" "}
			<input
				value={searchString}
				onChange={(e) => {
					setSearchString(e.target.value);
				}}
			/>
			{searchString !== "" ? (
				searchDataLoading || searchDataPending ? (
					<Loading />
				) : (
					<UserTable
						tableID="search_users"
						userData={searchData["results"]}
						buttonText="Add"
						button={true}
						buttonClass="btn btn-primary"
					/>
				)
			) : null}
		</>
	);
};

export default UserSelector;
