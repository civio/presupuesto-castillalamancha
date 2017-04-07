// Theme custom js methods
$(document).ready(function(){

  var addSankeyAlert = function(selector) {
    var str = {
      'es': 'Se representan tanto los ingresos como los gastos no financieros (Capítulos del I al VII)',
    };
    var cont = $(selector);
    if (cont.size() > 0) {
      cont.prepend('<div class="alert alert-data-update">' + str[$('html').attr('lang')] + '</div>');
    }
  };

  addSankeyAlert('.sankey-container');
});