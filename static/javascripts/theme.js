// Theme custom js methods
$(document).ready(function(){

  // add sankey alert
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

  // add treemap alert
  var addTreemapAlert = function() {
    var str = {
      chapter_incomes: {
        'es': 'Ingresos por capítulo'
      },
      article_incomes: {
        'es': 'Ingresos por artículo'
      },
      chapter_expenses: {
        'es': 'Gastos por capítulo'
      },
      article_expenses: {
        'es': 'Gastos por artículo'
      }
    };

    $('.policies-chart #budget-summary').prepend('<div class="alert alert-incomes">'+str.chapter_incomes[ $('html').attr('lang') ]+'</div>');
    $('.policies-chart #budget-summary').append('<div class="alert alert-incomes alert-articles">'+str.article_incomes[ $('html').attr('lang') ]+'</div>');
    $('.policies-chart #budget-summary').prepend('<div class="alert alert-expenses">'+str.chapter_expenses[ $('html').attr('lang') ]+'</div>');
    $('.policies-chart #budget-summary').append('<div class="alert alert-expenses alert-articles">'+str.article_expenses[ $('html').attr('lang') ]+'</div>');

  };

  // show / hide treemap alert based on selected tab
  var setupTreemapAlert = function(state) {
    if (state == 'income') {
      $('.policies-chart #budget-summary .alert-incomes').show();
      $('.policies-chart #budget-summary .alert-expenses').hide();
    } else if (state == 'expense') {
      $('.policies-chart #budget-summary .alert-incomes').hide();
      $('.policies-chart #budget-summary .alert-expenses').show();
    } else {
      $('.policies-chart #budget-summary .alert-incomes').hide();
      $('.policies-chart #budget-summary .alert-expenses').hide();
    }
  };

  // add section labels to institutional budget summary, see #430
  var setupBudgetSummaryLabels = function(state) {
    if (state == 'institutional') {
      $('.budget-summary-item-M .budget-summary-label').text('Servicio de salud');
      $('.budget-summary-item-5 .budget-summary-label').text('Deuda pública');
      $('.budget-summary-item-A .budget-summary-label').text('Educación, Cultura y Deportes');
      $('.budget-summary-item-D .budget-summary-label').text('Agricultura, Medio Ambiente y Desarrollo Rural');
      $('.budget-summary-item-G .budget-summary-label').text('Bienestar Social');
    }
  };

  // custom labels for year selector
  var addYearSelectorCustomLabels = function(){
    var str2017 = {
      'es': 'primer semestre'
    };
    var str2018 = {
      'es': 'primer semestre'
    };

    $('.data-controllers .layout-slider .slider .slider-tick-label').each(function(){
      var val = $(this).html();
      if (val === '2017') {
        $(this).html(val + '<br/><small><i> ('+ str2017[ $('html').attr('lang') ] +')</i></small>');
      };
      if (val === '2018') {
        $(this).html(val + '<br/><small><i> ('+ str2018[ $('html').attr('lang') ] +')</i></small>');
      };
    });
  };


  addYearSelectorCustomLabels();

  addTreemapAlert();

  setupTreemapAlert($('section').data('tab'));
  setupBudgetSummaryLabels($('section').data('tab'));

  $(window).bind('hashchange', function(e) {
    var state = $.deparam.fragment();
    setupTreemapAlert(state.view);
    setupBudgetSummaryLabels(state.view);
  });

  $('#year-selection').on('change', function() {
    var state = $.deparam.fragment();
    setupBudgetSummaryLabels(state.view);
  });
});
