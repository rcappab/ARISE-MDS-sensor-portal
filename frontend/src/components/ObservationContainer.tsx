import React, { useContext } from "react";

import { getData } from "../utils/FetchFunctions.js";
import Loading from "./Loading.tsx";
import { useQuery, keepPreviousData } from "@tanstack/react-query";
import AuthContext from "../context/AuthContext.jsx";
import ObservationTable from "./ObservationTable.tsx";
import { useSearchParams } from "react-router-dom";
import { ObsEditModeContext } from "../context/ObsModeContext.jsx";
import ObservationForm from "./ObservationForm.tsx";

interface ObserationContainerProps {
	fileData: object;
	canAnnotate: boolean;
}

const ObservationContainer = ({
	fileData,
	canAnnotate,
}: ObserationContainerProps) => {
	const { authTokens, user } = useContext(AuthContext);
	const { obsEditMode, setObsEditMode } = useContext(ObsEditModeContext);

	//setObsEditMode(obsEditMode && canAnnotate ? true : false);

	if (isLoading || isPending || isRefetching) {
		return <Loading />;
	}

	return (
		<div>
			{obsEditMode ? (
				<ObservationForm
					initialAllObsData={data}
					fileData={fileData}
					onSubmit={refetch}
				/>
			) : (
				<ObservationTable allObsData={data} />
			)}

			<button
				onClick={() => {
					setObsEditMode(!obsEditMode);
				}}
			>
				{canAnnotate ? (obsEditMode ? "Cancel" : "Edit mode") : null}
			</button>
		</div>
	);
};

//obs form components

//track edit rows
//deleted rows
//added rows
//autocomplete species
//non owned annotations locked except for validate button

export default ObservationContainer;
