/**
 * jQuery calendar - v1.0
 * auth: shenmq
 * E-mail: shenmq@yuchengtech.com
 * website: shenmq.github.com
 */
 
(function($, undefined) {
	
	var Month = function(year, month, currentDay) {
		this.year = year ;
		this.month = month;
		
		if(month < 0 ) {
			this.year -=1;
			this.month = 11;
		}
		
		if(month > 11) {
			this.year +=1;
			this.month = 0;
		}
		
		this.isLeapYear = this.getLeapYear();
		this.Months = this.getMonths();
		var firstDay = new Date(this.year, this.month, 1);
		this.days = this.getDays(this.month);
		
		this.firstWeekdayIndex = firstDay.getDay();
		if(this.firstWeekdayIndex === 0)
			this.firstWeekdayIndex = 7;
		if(currentDay)
			this.currentDay = currentDay;
		
		this.previousMonthLastDay = this.getPreviousMonthLastDay(this.month);
		this.firstWeekday = this.firstWeekdayIndex;
		this.lastWeekday = this.getLastWeekday();
	}
	
	
	Month.prototype = {
		constructor: Month,
		
		getMonth: function(index, Months) {
			if (index <= 12 && index >= -1) {
				if (index == 12) {
					this.yearChanged = 1;
					this.monthIndex = 0;
					return Months[0].name;
				} 
				else if (index == -1) {
					this.yearChanged = -1;
					this.monthIndex = 11;
					return Months[11].name;
				} 
				else {
					this.monthIndex = index;
					return Months[index].name;
				}
			} 
			else {
				this.monthIndex = -42;	//Invalid monthIndex
				return 'Invalid';
			}
		},
		
		getMonths: function() {
			return [31, (this.isLeapYear === true) ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
		},
		
		getDays: function(month) {
			if (month >= 0 && month < 12)
				return this.Months[month];
		},
		
		getWeekday: function(index, Weekdays) {
			if (index <= 7 && index >= -1) {
				if(index == 7) {
					return Weekdays[0];
				} 
				else if(index == -1) {
					return Weekdays[6];
				} 
				else {
					return Weekdays[index];
				}
			} 
			else {
				return 'Invalid';
			}
		},
		
		getFirstWeekdayIndex: function(Weekdays) {
			for (var i = 0; i < Weekdays.length; i++) {
				if (Weekdays[i] ===  this.firstWeekday) {
					return i;
				}
			}
			return -1;
		},
		
		getPreviousMonthLastDay: function(month) {
			var lastMonth = month - 1;
			return this.Months[lastMonth < 0 ? 11 : lastMonth];
		},
		
		getLastWeekday: function(Weekdays) {
			var lastweekday = this.firstWeekday;
			lastweekday += this.days % 7;
			lastweekday = lastweekday % 7;
			return lastweekday;
		},
		
		
		getLeapYear: function() {
			if (this.year % 4 === 0) {
				if (this.year % 100 !== 0) {
					return true;
				} 
				else {
					return false;
				}
			} 
			else {
				return false;
			}
		},
		
		renderDays: function() {
			var padding = this.firstWeekdayIndex;
			var lastMonthDay = this.previousMonthLastDay - padding + 1;
			var firstMonthDay = 1;
			var days = 1;
			var html = '<div class="grid_content"><div class="weeks">'
            this.startDate = this.year + '-' + this.month + '-' + lastMonthDay
			for (var i = 1; i <= 6; i++) {
				html += '<div class="week"><div class="dates_wrapper"><div class="dates">';
				for(var j = 1; j <= 7; j++) {
					if (padding-- > 0) {
						html += "<div class='date' data-date='" + new Date(this.year ,this.month - 1, lastMonthDay).format('yyyy-mm-dd') 
                            + "'><div class='day'>" + (lastMonthDay++) + "</div></div>";
						continue;
					}
					if (days > this.days) {
						html += "<div class='date' data-content='next' data-date='" + new Date(this.year ,this.month + 1 , firstMonthDay ).format('yyyy-mm-dd') 
                            + "'><div class='day' >" + (firstMonthDay++) + "</div></div>";
                        this.endDate =  this.year + "-" + (this.month + 2) + "-" + firstMonthDay
						continue;
					}
					if (days == this.currentDay) {
						html += "<div class='date current_month today' data-date='" +new Date(this.year ,this.month, firstMonthDay ).format('yyyy-mm-dd') 
                            + "'><div class='day'>" + (days++) + "</div></div>";
					} 
					else {
						html += "<div class='date current_month' data-date='" + new Date(this.year ,this.month, days ).format('yyyy-mm-dd') 
                            + "'><div class='day'>" + (days++) + "</div></div>";
					}
				}
				html += "</div></div></div>";
			}
			html += "</div>";
			return html;
		}
	}
	
	var MyCalendar = function ( element, options ) {
		
		this.init('', element, options);
	}
	
	MyCalendar.prototype = {
		constructor: MyCalendar,
		
		localization: { // Default regional settings
			closeText: 'Done', // Display text for close link
			prevText: 'Prev', // Display text for previous month link
			nextText: 'Next', // Display text for next month link
			currentText: 'Today', // Display text for current month link
			monthNames: ['January','February','March','April','May','June',
				'July','August','September','October','November','December'],
			monthNamesShort: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
			dayNames: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'], // For formatting
			dayNamesShort: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'], // For formatting
			dayNamesMin: ['Su','Mo','Tu','We','Th','Fr','Sa'], // Column headings for days starting at Sunday
			weekHeader: 'Wk', // Column header for week of the year
			dateFormat: 'mm/dd/yy', // See format options on parseDate
			firstDay: 0, // The first day of the week, Sun = 0, Mon = 1, ...
			isRTL: false, // True if right-to-left language, false if left-to-right
			showMonthAfterYear: false, // True if the year select precedes month, false for month then year
			yearSuffix: '' // Additional text to append to the year in the month headers
		},
		
		init: function ( type, element, options ) {
			this.type = type;
			this.$element = $(element);
			this.options = options;
			var self = this;
			
			this.now = new Date();
			this.year = this.options.year ? this.options.year : this.now.getFullYear();
			
			this.currentMonth = this.options.month ? this.options.month : this.now.getMonth();
			
			
			var calendarObj = $(this.renderCalendar());
			calendarObj.height(this.options.headHeight);
			
			$('.prev', calendarObj).bind('click.myCalendar', function(event) {
				return self.prevMonth();
			});
			
			$('.next', calendarObj).bind('click.myCalendar', function(event) {
				return self.nextMonth();
			});
			
			var month = new Month(this.year, this.currentMonth, this.now.getDate());
			
			var width = this.$element.width();
			var height = this.$element.height() - this.options.headHeight;
			
			this.currentIndex = 0;
			
			this.monthOjb = $(month.renderDays());
			
			$('.date', this.monthOjb).bind('click.myCalendar-day', function(event) {
				return self.dayClick(event);
			});
			
			$(this.options.body, this.$element).append(calendarObj);
			$(this.options.body, this.$element).append(this.monthOjb);

            self.initEvent(month)
		},

        initEvent: function(month) {
            var startDate = month.startDate
            var endDate = month.endDate

            var that = this
            function callback(reponseData) {
                var todoItems = reponseData.todoItems
                for(var i in todoItems) {
                    var todoItem = todoItems[i]
                    var date = todoItem.deadline.substring(0,10)
                    var $dayElement = $('[data-date=' + date + ']', that.$element)
                    var $todoContainer = $('.todos', $dayElement)
                    if($todoContainer.length == 0 ) {
                        $todoContainer = $('<div class="events todos "></div>')
                        $dayElement.append($todoContainer) 
                    }
                    var description = todoItem.description
                    if(description.length > 7 )
                        description = description.substring(0, 7) + '...'
                    var $todoElement = $('<div class="event todo " data-id="45285047" data-behavior="calendar_todo"><span class="wrapper event">'
                        + '<input type="checkbox" value="1" data-behavior="toggle_todo" data-url="/project/' + todoItem.project_id 
                        + '/todolist' + todoItem.todolist_id + '/todoitem/' + todoItem.id + '/done">'
                        + '<span class="content" title="' + todoItem.description  + '" style="color:#3185c5">' + description + '</span></span></div>')
                    $todoContainer.append($todoElement)
                }
            }
            $.lily.ajax({
                url : this.options.url,
                data : {start_date: startDate, end_date: endDate},
	        	type: 'get',
	        	processResponse : callback
	        });
        },
		
		dayClick: function(event) {
            var $target = $(event.target)
            if(!$target.hasClass("date"))
                return
			var day = $target.attr('data-date');
			switch(day) {
				case 'next':
					this.nextMonth();
					break;
				case 'prev':
					this.prevMonth();
					break;
				default:
					if(this.options.selector) {
						var date = $.lily.format.parseDate(day, "yyyy-mm-dd")
						this.options.selector($target, date);
					}
			}
		},
		
		prevMonth: function() {
			var self = this;
			this.currentMonth -= 1;
			
			if(this.currentMonth < 0 ) {
				this.year -=1;
				this.currentMonth = 11;
			}
			this.updateCalendarHead();
			
			var currentDay = null
			if(this.currentMonth == this.now.getMonth())
				currentDay = this.now.getDate()
			var month = new Month(this.year, this.currentMonth , currentDay);
			
			
			var oldMonthObj = this.monthOjb;
			this.monthOjb = $("<div class='lily-days-container'>" + month.renderDays() + "</div>");
			
			$('td', this.monthOjb).bind('click.myCalendar-day', function(event) {
				return self.dayClick(event);
			});
			
			this.$element.append(this.monthOjb);
				
			oldMonthObj.remove();
		},
		
		nextMonth: function() {
			var self = this;
			this.currentMonth += 1;
			
			if(this.currentMonth > 11) {
				this.year +=1;
				this.currentMonth = 0;
			}
			
			this.updateCalendarHead();
			
			var currentDay = null
			if(this.currentMonth == this.now.getMonth())
				currentDay = this.now.getDate()
			var month = new Month(this.year, this.currentMonth , currentDay);
			
			var oldMonthObj = this.monthOjb;
			this.monthOjb = $("<div class='lily-days-container'>" + month.renderDays() + "</div>");
			
			$('td', this.monthOjb).bind('click.myCalendar-day', function(event) {
				return self.dayClick(event);
			});
			
			this.$element.append(this.monthOjb);
				
			oldMonthObj.remove();
		},
		
		buildCalendarHead: function() {
			var monthHtml ;
			if(this.localization.showMonthAfterYear)
				monthHtml = this.year + this.localization.yearSuffix + this.localization.monthNames[this.currentMonth];
			else
				monthHtml = this.localization.monthNames[this.currentMonth] + ' ' + this.year + this.localization.yearSuffix;
			return monthHtml;
		},
		
		updateCalendarHead: function() {
			var monthHtml = this.buildCalendarHead();
			var headObj = $(this.options.title, this.$element);
			headObj.text(monthHtml);
		},
		
		renderCalendar: function () {
			//Template for Calendar
			var monthHtml = this.buildCalendarHead();
			
            this.updateCalendarHead()
			var html = "<div class='days_of_week'><div class='days'>"
			for(var i = 0; i < 	this.localization.dayNamesMin.length; ++i) {
				html += '<div class="day" >' + this.localization.dayNamesMin[i] + "</div>";
			}
			html += "</div></div>";
			return html;
		}
	}
	
	$.fn.myCalendar = function ( option ) {
    	return this.each(function () {
			var $this = $(this), 
				data = $this.data('myCalendar'), 
				options = $.extend({}, $.fn.myCalendar.defaults, $this.data(), typeof option == 'object' && option);
      		if (!data) 
      			$this.data('myCalendar', (data = new MyCalendar(this, options)));
      		if (typeof option == 'string') 
      			data[option]();
    	});
  	}

  	$.fn.myCalendar.Constructor = MyCalendar;
  	
  	$.fn.myCalendar.defaults = {
  		headHeight: 37,
  		target: null,
  		selector: null
  	}
})(jQuery);
