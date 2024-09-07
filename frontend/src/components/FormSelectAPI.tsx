import React, { useContext } from "react";
import FormSelect from "./FormSelect.tsx";
import { useQuery, useMutation } from "@tanstack/react-query";
import AuthContext from "../context/AuthContext";
import { getData, postData } from "../utils/FetchFunctions";

interface Props {
	name: string;
	id: string;
	defaultvalue: [string];
	label: string;
	choices: [];
	isSearchable?: boolean;
	isClearable?: boolean;
	apiURL: string;
	valueKey: string;
	labelKey: string;
	multiple?: boolean;
	creatable?: boolean;
	handleChange?: () => void;
}

const FormSelectAPI = ({
	name,
	id,
	defaultvalue,
	label,
	choices = [],
	isSearchable = true,
	isClearable = true,
	apiURL,
	valueKey,
	labelKey,
	multiple = false,
	creatable = false,
	handleChange = () => {},
}: Props) => {
	const { authTokens } = useContext(AuthContext);

	const getDataFunc = async () => {
		if (apiURL === "") {
			return [];
		}
		let response_json = await getData(apiURL, authTokens.access);
		let newOptions = response_json.map((x) => {
			return { value: x[valueKey], label: x[labelKey] };
		});
		let allOptions = choices.concat(newOptions);
		//console.log(allOptions);
		return allOptions;
	};

	const { data, isLoading, refetch } = useQuery({
		queryKey: [apiURL],
		queryFn: getDataFunc,
	});

	const handleCreate = async (newvalue: string) => {
		let results = await doCreate.mutateAsync(newvalue);
		let newoption = { label: results[labelKey], value: results[valueKey] };
		return newoption;
	};

	const doCreate = useMutation({
		mutationFn: (inputValue) => newPOST(inputValue),
	});

	const newPOST = async (inputValue) => {
		let newData = {};
		newData[labelKey] = inputValue;
		let response_json = await postData(apiURL, authTokens.access, newData);
		console.log(response_json);
		refetch();
		return response_json;
	};

	return (
		<FormSelect
			name={name}
			id={id}
			defaultvalue={isLoading ? null : defaultvalue}
			label={label}
			choices={isLoading ? null : data}
			isLoading={isLoading}
			isSearchable={isSearchable}
			multiple={multiple}
			creatable={creatable}
			handleCreate={handleCreate}
			handleChange={handleChange}
			isClearable={isClearable}
		/>
	);
};

export default FormSelectAPI;
