const validObjects = ["deployment", "device", "project", "datafile"];

const nameKeys = {
	deployment: "deployment_deviceID",
	device: "deviceID",
	project: "projectID",
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
