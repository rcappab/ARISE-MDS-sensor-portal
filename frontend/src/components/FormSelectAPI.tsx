import React, { useContext } from "react";
import FormSelect from "./FormSelect.tsx";
import { useQuery } from "@tanstack/react-query";
import AuthContext from "../context/AuthContext";
import getData from "../utils/FetchFunctions";

interface Props {
	name: string;
	id: string;
	defaultvalue: string;
	label: string;
	choices: [];
	isSearchable: boolean;
	apiURL: string;
	valueKey: string;
	labelKey: string;
}

const FormSelectAPI = ({
	name,
	id,
	defaultvalue,
	label,
	choices,
	isSearchable,
	apiURL,
	valueKey,
	labelKey,
}: Props) => {
	const { authTokens } = useContext(AuthContext);

	const getDataFunc = async () => {
		let response = await getData(apiURL, authTokens.access);
		let response_json = await response.json();
		let newOptions = response_json.map((x) => {
			return { value: x[valueKey], label: x[labelKey] };
		});
		let allOptions = choices.concat(newOptions);
		console.log(allOptions);
		return allOptions;
	};

	const { data, isLoading } = useQuery({
		queryKey: [apiURL],
		queryFn: getDataFunc,
	});

	return (
		<FormSelect
			name={name}
			id={id}
			defaultvalue={defaultvalue}
			label={label}
			choices={data}
			isLoading={isLoading}
			isSearchable={isSearchable}
		/>
	);
};

export default FormSelectAPI;
