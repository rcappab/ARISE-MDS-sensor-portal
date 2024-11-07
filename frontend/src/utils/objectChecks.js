const validObjects = ["deployment", "device", "project", "datafile"];

const nameKeys = {
	deployment: "deployment_device_ID",
	device: "device_ID",
	project: "project_ID",
	datafile: "filename",
};

const validGalleries = {
	deployment: ["datafile"],
	device: ["deployment", "datafile"],
	project: ["deployment", "datafile"],
	datafile: [],
};

export const getNameKey = function (objectType) {
	return nameKeys[objectType];
};

export const getValidGalleries = function (fromObject) {
	return validGalleries[fromObject];
};

export const getValidObject = function (objectType) {
	return validObjects.includes(objectType);
};
