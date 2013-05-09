/**
 * jQuery format - v1.0
 * auth: shenmq
 * E-mail: shenmq@yuchengtech.com
 * website: shenmq.github.com
 *
 */
 
(function( $, undefined ) {
	
	$.lily.param = $.lily.param || {};
	
	$.extend( $.lily.param, {
		OPERATION_TYPE :{
            '0':'创建', 
            '1':'删除', 
            '2':'编辑', 
            '3':'查询', 
            '4':'回复', 
            '5':'开始', 
            '6':'暂停', 
            '7':'完成'
		},

        TARGET_TYPE: {
            '0':'项目', 
            '1':'讨论', 
            '2':'评论', 
            '3':'任务列表', 
            '4':'任务', 
            '5':'用户'
        },

		getSelect: function( appName, selectCode, filter, blankSelect ) {
			var html = "";
			var map = $.lily.param[ appName ];
			if ( !map ) {
				alert( "param: " + appName + " not defined!");
				return null;
			}
			if(blankSelect)
				html += "<option value=\"\">请选择</option>";
			
			for(var key in map){
				var value = map[key];
				if(filter) {
					if(filter.include(key))
						continue;
				}
				if ( selectCode && selectCode == key ) {
					html += "<option value=\""+key+"\" selected=\"selected\">"+value+"</option>";
				}
				else {
					html += "<option value=\""+key+"\" >"+value+"</option>";
				}
			}
			return html;
		},
		
		getDisplay: function( appName, appValue ){
		//	console.log(appName);
			var map = $.lily.param[ appName ];
		//	console.log(map);
			if ( !map ) {
				//alert( "Liana.param: " + appName + " not defined!");
				return null;
			}
			return map[appValue];
		}
		
	});
	
})(jQuery)
