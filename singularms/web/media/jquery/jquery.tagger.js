/*
    Tagger Widget v1.0
    Copyright (C) 2008 Chris Iufer (chris@iufer.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>
*/

(function($){
	
	$.fn.addTag = function(v){
		var r = v.split(',');
		for(var i in r){
			n = r[i].replace(/([^a-zA-Z0-9\s\-\_+])|^\s|\s$/g, '');
			if(n == '') return false;
			var fn = $(this).data('name');
			var i = $('<input type="hidden" />').attr('name',fn).val(n);
			var t = $('<li />').text(n).addClass('tagName')
				.click(function(){
					// remove
					var hidden = $(this).data('hidden');
                    var list = $(this).data('listTagger');
                    list.splice(jQuery.inArray($(this).html(),list),1);
					$(hidden).remove();
					$(this).remove();
				})
				.data('hidden',i);
            $(t).data('listTagger',$(this).data('listTagger'));
			var l = $(this).data('list');
			$(l).append(t).append(i);
		}
	};
	


/*$.fn.prepareTagger = function(){
	$('.tagger').each(function(i){
        alert('tagger');
		$(this).data('name', $(this).attr('name'));	
		$(this).removeAttr('name');
		var b = $('<button type="button">Add</button>').addClass('tagAdd')
			.click(function(){
				var tagger = $(this).data('tagger');
				$(tagger).addTag( $(tagger).val() );
				$(tagger).val('');
				$(tagger).stop();
			})
			.data('tagger', this);
		var l = $('<ul />').addClass('tagList');
		$(this).data('list', l);			
		$(this).after(l).after(b);
	})
	.bind('keypress', function(e){
		if( 13 == e.keyCode){
			//console.log(e.keyCode);
			$(this).addTag( $(this).val() );
			$(this).val('');
			$(this).stop();
			return false;
		}
	});
};*/

$.fn.Tagger = function(options){
    if (options == undefined){
        options = {};
    }
    if (options['msg']==undefined){
        options['msg'] = "The number {val} is already in list of mobile";
    }
    $(this).data('name', $(this).attr('name'));
    $(this).removeAttr('name');
    $(this).data('listTagger',new Array());
	var b = $('<button type="button">Add</button>').addClass('tagAdd')
			.click(function(){
				var tagger = $(this).data('tagger');
                var list = $(this).data('listTagger');
                if ($(tagger).val()!=''){
                    if (jQuery.inArray($(tagger).val(),list)==-1){
                        $(tagger).addTag( $(tagger).val() );
                        list.push($(tagger).val());
                    
                    }else{
                        alert($.format(options['msg'],{val:+$(tagger).val()}));
                    }
                }
                $(tagger).val('');
                $(tagger).stop();
			})
			.data('tagger', this);
	var l = $('<ul />').addClass('tagList');
	$(this).data('list', l);
	$(this).after(l).after(b);
    $(this).blur(function(){
        var list = $(this).data('listTagger');
        if ($(this).val()!=''){
            if (jQuery.inArray($(this).val(),list)==-1){
                $(this).addTag( $(this).val() );
                list.push($(this).val());
            
            }else{
                alert($.format(options['msg'],{val:$(this).val()}));
            }
        }
        $(this).val('');
        $(this).stop();
    });
};
})(jQuery);