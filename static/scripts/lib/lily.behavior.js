!function ($) {

  $(document).on('mouseover.behavior.data-api', '[data-behavior^=has_hover_content]', function (e) {
    var $btn = $(e.target)
    if (!($btn.attr('data-behavior') == 'has_hover_content')) $btn = $btn.closest('[data-behavior=has_hover_content]')
    var $content = $('[data-behavior*=hover_content]', $btn)
    $content.show()
  })

  $(document).on('mouseout.behavior.data-api', '[data-behavior^=has_hover_content]', function (e) {
    var $btn = $(e.target)
    if (!($btn.attr('data-behavior') == 'has_hover_content')) $btn = $btn.closest('[data-behavior=has_hover_content]')
    var $content = $('[data-behavior*=hover_content]', $btn)
    $content.hide()
  })
  
}(window.jQuery);
