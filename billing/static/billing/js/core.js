function gridActionBySelectedId(gridName, baseUrl, paramsToReplace, columnName, noSelectionError){
	var myGrid = $('#'+gridName),
		selRowId = myGrid.jqGrid ('getGridParam', 'selrow'),
		celValue = myGrid.jqGrid ('getCell', selRowId, columnName); 
	if (celValue == null){
		alert(noSelectionError);
	}
	else{
		newUrl = baseUrl.replace(paramsToReplace, celValue);
		window.open(newUrl, "_self");
		// return newUrl
	}
	
}