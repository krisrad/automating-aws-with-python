
//BUDGET CONTROLLER
var budgetController = (function() {

    var Expense = function(id, description, value) {
        this.id = id;
        this.description = description;
        this.value = value;
        this.percentage = -1;
    };

    Expense.prototype.calcPercentage = function(totalIncome) {
        if (totalIncome > 0) {
            this.percentage = Math.round((this.value / totalIncome) * 100);
        } else {
            this.percentage = -1;
        }
    }

    Expense.prototype.getPercentage = function() {
        return this.percentage;
    }
    
    var Income = function(id, description, value) {
        this.id = id;
        this.description = description;
        this.value = value;
    };

    var calculateTotal = function(type) {
        data.totals[type] = 0;
        data.allItems[type].forEach(function(d) {
            data.totals[type] += d.value;
        })
    };

    var data = {
        allItems: {
            exp: [],
            inc: []
        },
        totals: {
            exp:0,
            inc:0
        },
        budget: 0,
        percentage: -1
    };

    return {
        addItem: function(type, desc, val) {
            var newItem, ID;
            //create a new id
            if (data.allItems[type].length > 0) {
                ID = data.allItems[type][data.allItems[type].length-1].id + 1;
            } else {
                ID = 0;
            }
            
            //create a new item based on inc or exp item type
            if (type === 'exp') {
                newItem = new Expense(ID, desc, val);                
            } else if (type === 'inc') {
                newItem = new Income(ID, desc, val);                
            }

            //push it into data structure
            data.allItems[type].push(newItem);

            //return the new element
            return newItem;
        },

        deleteItem : function(type, id) {
            var ids, index;
            ids = data.allItems[type].map(function(d) {
                return d.id;
            });
            index = ids.indexOf(id);
            if (index !== -1) {
                data.allItems[type].splice(index, 1);
            }
        },

        calculateBudget: function() {
            // calculate total income and expenses
            calculateTotal('inc');
            calculateTotal('exp');
            // calculate the budget: income - expenses
            data.budget = data.totals.inc - data.totals.exp;
            // calculate the percentage of income that we spent
            if (data.totals.inc > 0) {
                data.percentage = Math.round((data.totals.exp / data.totals.inc) * 100);
            } else {
                data.percentage = -1;
            }
        },

        calculatePercentages: function() {
            data.allItems.exp.forEach(function(d) {
                d.calcPercentage(data.totals.inc);
            });
        },

        getPercentages: function() {
            var allPerc = data.allItems.exp.map(function(d) {
                return d.getPercentage();
            });
            return allPerc;
        },

        getBudget: function() {
            return {
                budget: data.budget,
                totalInc: data.totals.inc,
                totalExp: data.totals.exp,
                percentage: data.percentage
            }
        },

        testing: function() {
            console.log(data);
        }
    }

})();


// UI CONTROLLER
var UIController = (()=>{

    var DOMstrings = {
        inputType: '.add__type',
        inputDescription: '.add__description',
        inputValue: '.add__value',
        inputBtn: '.add__btn',
        incomeContainer: '.income__list',
        expenseContainer: '.expenses__list',
        budgetLabel: '.budget__value',
        incomeLabel: '.budget__income--value',
        expenseLabel: '.budget__expenses--value',
        percentageLabel: '.budget__expenses--percentage',
        container: '.container',
        expensesPercentageLabel: '.item__percentage',
        dateLabel: '.budget__title--month'
    };

    formatNumber = function(num, type) {
        var numSplit, int, dec;

        num = Math.abs(num);
        num = num.toFixed(2);
        numSplit = num.split('.');
        int = numSplit[0];
        if (int.length > 3) {
            int = int.substr(0,int.length-3) + ',' + int.substr(int.length-3, 3);
        }
        dec = numSplit[1];
        return (type==='exp'?'-':'+') + ' ' + int + '.' + dec;
    };

    return {
        getDomStrings: function() {
            return DOMstrings;
        },
        getinput: () => {
            return {
                type : document.querySelector(DOMstrings.inputType).value, // will be either inc or exp
                description : document.querySelector(DOMstrings.inputDescription).value,
                value : parseFloat(document.querySelector(DOMstrings.inputValue).value)
            };            
        },
        addListItem: function(obj, type) {
            var html, newHtml, element;

            // create HTML string with placeholder text
            if (type === 'inc') {
                element = DOMstrings.incomeContainer;
                html = '<div class="item clearfix" id="inc-%id%"><div class="item__description">%description%</div>' +
                        '<div class="right clearfix"><div class="item__value">%value%</div><div class="item__delete">' + 
                        '<button class="item__delete--btn"><i class="ion-ios-close-outline"></i></button></div></div></div>';
            } else {
                element = DOMstrings.expenseContainer;
                html = '<div class="item clearfix" id="exp-%id%"><div class="item__description">%description%</div>' + 
                        '<div class="right clearfix"><div class="item__value">%value%</div><div class="item__percentage">21%</div>' + 
                        '<div class="item__delete"><button class="item__delete--btn"><i class="ion-ios-close-outline"></i></button></div></div></div>';
            }                                

            // Replace the placeholder text with some actual data
            newHtml = html
                        .replace('%id%', obj.id)
                        .replace('%description%',obj.description)
                        .replace('%value%',formatNumber(obj.value, type));

            // insert the html into the DOM
            document.querySelector(element).insertAdjacentHTML('beforeend', newHtml);
        },
        deleteListItem: function(selectorId) {
            var el = document.getElementById(selectorId);
            el.parentNode.removeChild(el);
        },
        clearFields: function() {
            var fields;
            fields = document.querySelectorAll(DOMstrings.inputDescription + ', ' + DOMstrings.inputValue);
            var fieldsArray = Array.prototype.slice.call(fields);

            fields.forEach(function(d) {
                d.value = '';
            });

            fields[0].focus();
        },

        displayBudget: function(obj) {
            var type;
            obj.budget > 0 ? type = 'inc' : type = 'exp';

            document.querySelector(DOMstrings.budgetLabel).textContent = formatNumber(obj.budget, type);
            document.querySelector(DOMstrings.incomeLabel).textContent = formatNumber(obj.totalInc, 'inc');
            document.querySelector(DOMstrings.expenseLabel).textContent = formatNumber(obj.totalExp, 'exp');
            if (obj.percentage > 0) {
                document.querySelector(DOMstrings.percentageLabel).textContent = obj.percentage + '%';
            } else {
                document.querySelector(DOMstrings.percentageLabel).textContent = '---';
            }            
        },

        displayMonth: function() {
            var now, year, months, month;
            now = new Date();
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
            month = now.getMonth();
            year = now.getFullYear();
            document.querySelector(DOMstrings.dateLabel).textContent = months[month] + ' ' + year;
        },

        displayPercentages: function(percentages) {
            var fields = document.querySelectorAll(DOMstrings.expensesPercentageLabel);
            fields.forEach(function(d,i) {
                if (percentages[i] > 0) {
                    d.textContent = percentages[i]+'%';
                } else {
                    d.textContent = '---';
                }
                
            });
        },

        changedType: function() {
            var fields = document.querySelectorAll(
                DOMstrings.inputType + ',' + 
                DOMstrings.inputDescription + ',' +
                DOMstrings.inputValue);
            
            fields.forEach(function(d) {
                d.classList.toggle('red-focus');
            });

            document.querySelector(DOMstrings.inputBtn).classList.toggle('red');
        }
    };

})();

// GLOBAL APP CONTROLLER
var controller = ((budgetCtrl, uiCtrl)=> {

    var setupEventListeners = function() {
        var DOM = uiCtrl.getDomStrings();
        document.querySelector(DOM.inputBtn).addEventListener('click', ctrlAddItem);
        document.addEventListener('keypress', (event)=> {
            if (event.keyCode === 13 || event.which === 13) {
                ctrlAddItem();
            }
        });
        document.querySelector(DOM.container).addEventListener('click', ctrlDeleteItem);
        document.querySelector(DOM.inputType).addEventListener('change', UIController.changedType);
    }

    var updateBudget = function() {
        
        //1. Calculate the budget
        budgetController.calculateBudget();

        //2. Return the budget
        var budget = budgetController.getBudget();

        //3. Display the budget on the UI
        UIController.displayBudget(budget);
    };

    var updatePercentages = function() {
        
        //1. calculate the percentages
        budgetController.calculatePercentages();

        //2. Read percentages from budget controller
        var percentages = budgetController.getPercentages();

        //3. update the ui with the new percentages
        UIController.displayPercentages(percentages);

    }

    var ctrlAddItem = function() {
        var input, newItem;

        //1. Get the field input data
        var input = uiCtrl.getinput();

        if (input.description !== '' && !isNaN(input.value) && input.value > 0) {
            //2. Add the item to the budget controller
            var newItem = budgetController.addItem(input.type, input.description, input.value);            

            //3. Add the item to the UI
            UIController.addListItem(newItem, input.type);

            //4. clear the fields
            UIController.clearFields();

            //5. calculate and update budget
            updateBudget();

            //6. Calculate and update percentages
            updatePercentages();
        }
    };

    var ctrlDeleteItem = function(event) {
        var itemID, splitId, type, id;
        itemID = event.target.parentNode.parentNode.parentNode.parentNode.id;
        if (itemID) {
            splitId = itemID.split('-');
            type = splitId[0];
            id = parseInt(splitId[1]);

            //1. delete item from the datastructure
            budgetController.deleteItem(type, id);

            //2. delete the item from UI
            UIController.deleteListItem(itemID);

            //3. Update and show new budget totals
            updateBudget();

            //4. Calculate and update percentages
            updatePercentages();
        }
    };

    return {
        init: function() {
            console.log("Application has started.");
            UIController.displayMonth();
            UIController.displayBudget({
                budget: 0,
                totalInc: 0,
                totalExp: 0,
                percentage: -1
            });
            setupEventListeners();
        }
    };

})(budgetController, UIController);

controller.init();