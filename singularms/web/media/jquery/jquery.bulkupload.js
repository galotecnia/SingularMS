/*
 * jQuery JavaScript Library v1.3.2
 * http://whynotonline.com/
 *
 * Copyright (c) 2009 Nivanka Fonseka
 * BSD licenses.
 * http://open.whynotonline.com/license/
 * 
 * This plugin is a handy tool which you can use to create bulk file uploaders in your HTML Forms
 * Feel free to use this on your websites, but please leave this message in the fies
 */

jQuery.fn.bulkupload = function(options) {

	$current = jQuery(this);
	$current.bind('change', fileSelected);
	$parent = $current.parent().parent();
	$parent.append("<div id='BulkUploaderList'></div>");
	jQuery('#BulkUploaderList').hide();
    options = options || {types:['gif','png']};
    jQuery.bulkUploadPlugin = {
        types : options.types,
        msg: options.msg
    }
  
};

function fileSelected(event){
	
	$current = event.target;
    var end = -1;
    jQuery.each(jQuery.bulkUploadPlugin.types,function(){
        if (jQuery($current).val().slice(-3) == this){
            end = 0;
            return;
        }
    });
    if (end == -1){
        alert(jQuery($current).val().slice(-3)+jQuery.bulkUploadPlugin.msg);
        jQuery($current).val('');
        return;
    }
	$class = jQuery($current).attr('class');
	$name = jQuery($current).attr('name');
	
	$filesAlreadySelected = jQuery('.BulkUploaderHidden');
	$filesAlreadySelected.each(
		function (){
			if(jQuery(this).val() == jQuery($current).val()){
				alert("That file is already in the list!");
				return;
			}	
		}
	);
	
	jQuery($current).attr('style', 'position:absolute; top: -3000px;');
	jQuery($current).addClass('BulkUploaderHidden');
	
	$list = jQuery('#BulkUploaderList');
	$listItem = '<p>' + jQuery($current).val() + ' <a class="BulkUploaderRemove" val="' + jQuery($current).val() + '" >X</a></p>';
	$list.append($listItem);
	
	
	$html = '<input type="file" name="' + $name +'" class="' + $class +'" />';
	$newinput = jQuery($html);
	$parent = jQuery($current).parent();
	$newinput.appendTo($parent);
	$newinput.bind('change', fileSelected);
	
	jQuery('.BulkUploaderRemove').bind('click', deleteFileSelected);
	if(jQuery('#BulkUploaderList').attr('style').indexOf('none') >= 0){
		jQuery('#BulkUploaderList').show();
	}
}

function deleteFileSelected(event){
	
	$current = jQuery(event.target);
	
	$filesAlreadySelected = jQuery('.BulkUploaderHidden');
	$filesAlreadySelected.each(
		function (){
			if(jQuery(this).val() == $current.attr('val')){
				jQuery(this).remove();
				$current.parent().remove();
				if(jQuery('#BulkUploaderList').html() == "")
					jQuery('#BulkUploaderList').hide();
				return;
			}	
		}
	);
}