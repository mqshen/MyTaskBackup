!function($) {

	"use strict"; // jshint ;_;

	var EditorTrigger = function(element, options) {
		this.$element = $(element)
		this.options = $.extend({}, $.fn.button.defaults, options)
		this.$target = this.$element.closest('.editable_container')
	}

	EditorTrigger.prototype = {
		init: function() {
            this.$editorContainer = this.$target.clone()
            this.$editorContainer.removeClass() 
            this.$editorContainer.addClass("edit_mode") 
            this.$editorContainer.css("display", "none")
            var $form = $('<form class="' + this.$target.attr("data-target-class") + '" method="post" action="' + this.$target.attr("href") + '" data-save="true"></form>')
			var self = this
			function doResponse(data) {
				$('.editable,.echo', self.$target).each(function(){
					var $this = $(this)
                    $.lily.fillHtml($this, data)
				})
				self.toggle()
			}
			$form.data('doResponse', doResponse);
			$('.editable', this.$editorContainer).each(function(){
				var $this = $(this)
				var $obj;
				var dataType = $this.attr("data-type");
				if(dataType == "textarea") {
					$obj = $('<textarea style="resize: none; overflow: hidden; min-height: 18px;" data-toggle="remote"></textarea>')
				}
                else if(dataType == "html") {
                    $obj = $this.clone()
                }
				else if(dataType == "file") {
					var fileUploadContainer = $('<div class="file_input_button">' 
						+ '<span class="prompt_graphic"></span><span class="file_input_container">'
						+ '<input type="file" name="file" style="opacity:0;height:80;cursor:pointer;font-size:0;position:absolute;">'
		                + '<a href="javascript:;" class="">上传</a>'
		                + '</span></div>')
					
					$obj = $this.clone()
					$obj.prepend(fileUploadContainer)
					self.$fileEditContainer = $('.file-list', $obj)
					
					$('[type="file"]', fileUploadContainer).bind("change", function() {
						var $this = $(this)
	                    $.ajaxFileUpload({
	                        url: $.lily.contextPath + '/attachment',
	                        secureuri: false,
	                        fileElement: $this,
	                        dataType: 'json',
	                        success: function (reponseData, status) {      
	                        	self.fileUploadCallback(reponseData)
	                        }
	                    })
	                })
				}
				else {
					$obj = $('<input type="text" >')
				}
				$obj.attr("name", $this.attr("name"))
				$obj.attr("id", $this.attr("id"))
				$obj.val($this.html().trim())
                $obj.appendTo($form)
			})
            this.$editorContainer.empty()
            $form.appendTo(this.$editorContainer)
			this.$editorContainer.insertAfter(this.$target)

            var $buttonObj = $('<p class="submit">'
                + '<button tabindex="1" class="btn btn-primary" id="btn-post" data-toggle="submit" data-disable-with="正在保存...">保存</button>' 
                + '<a tabindex="2" href="javascript:;" class="btn btn-x" id="link-cancel-post">取消</a></p>')
			$buttonObj.appendTo($form)
			var self = this
			$('#link-cancel-post', this.$editorContainer).click(function(){
				self.toggle()
			})
			this.initialized = true
		},
		
		fileUploadCallback: function(responseData) {
			
			if(responseData.file.imageFile) {
				var imageFile = $('<div class="file selected" data-toggle="select" data-content="'
					+ responseData.file.id + '" name="files"><div class="file-thumb"><a href="javascript:;" title="点击预览">'
					+ '<img class="image" alt="" src="' + $.lily.contextPath + '/attachment/' + responseData.file.url + '">'
					+ '</a></div>'
					+ '<a class="remove" data-toggle="remove" href="javascript:;">&nbsp;</a>'
					+ '</div>')
				var fileEditContainer = $('.file-images', this.$fileEditContainer)
				fileEditContainer.prepend(imageFile)
			}
			else {
				var otherFile = $('<div class="file selected" data-toggle="select" data-content="'
					+ responseData.file.id + '" name="files"><div class="file-thumb">'
					+ '<a href="' + $.lily.contextPath + '/attachment/' + responseData.file.url + '">'
					+ '<img alt="README" src="' + $.lily.contextPath + '/resources/images/file_extension_others.png"></a></div>'
					+ '<a class="remove" data-toggle="remove" href="javascript:;">&nbsp;</a>'
					+ '</div>')
				var fileEditContainer = $('.file-others', this.$fileEditContainer)
				fileEditContainer.prepend(otherFile)
			}
			
			
		},
		
		toggle: function() {
			if(!this.initialized)
				this.init()
			this.$target.toggle()
			this.$editorContainer.toggle()
		}

	}

	$.fn.editorTrigger = function(option) {
		return this
				.each(function() {
					var $this = $(this), data = $this.data('editorTrigger'), options = typeof option == 'object' && option
					if (!data)
						$this.data('editorTrigger', (data = new EditorTrigger(this, options)))
					data.toggle()
				})
	}

	$.fn.editorTrigger.defaults = {
		loadingText : 'loading...'
	}

	$.fn.editorTrigger.Constructor = EditorTrigger

	$(document).on('click.button.data-api', '[data-toggle^=editorTrigger]',
			function(e) {
				var $btn = $(e.target)
				e.preventDefault()
				$btn.editorTrigger("submit")
			})

}(window.jQuery);
