(function(global, factory) {
  typeof exports === 'object' && typeof module !== 'undefined' ? module.exports = factory(require('bootstrap')) : typeof define === 'function' && define.amd ? define(['bootstrap'], factory) : (global = typeof globalThis !== 'undefined' ? globalThis : global || self,
  global.perforge = factory(global.bootstrap));
}
)(this, (function() {
  'use strict';

  const docReady = e=>{
      "loading" === document.readyState ? document.addEventListener("DOMContentLoaded", e) : setTimeout(e, 1);
  };

  const camelize = e=>{
      const t = e.replace(/[-_\s.]+(.)?/g, ((e,t)=>t ? t.toUpperCase() : ""));
      return `${t.substr(0, 1).toLowerCase()}${t.substr(1)}`
  };

  const getData = (e,t)=>{
      try {
          return JSON.parse(e.dataset[camelize(t)])
      } catch (o) {
          return e.dataset[camelize(t)]
      }
  };

  const hasClass = (e,t)=>e.classList.value.includes(t);
  const addClass = (e,t)=>e.classList.add(t);
  const removeClass = (e,t)=>e.classList.remove(t);

  const setCookie = (e,t,o)=>{
      const r = new Date;
      r.setTime(r.getTime() + o),
      document.cookie = e + "=" + t + ";expires=" + r.toUTCString();
  };
  const getCookie = e=>{
      var t = document.cookie.match("(^|;) ?" + e + "=([^;]*)(;|$)");
      return t ? t[2] : t
  };
  const getRandomNumber = (e,t)=>Math.floor(Math.random() * (t - e) + e);

  const sendPostRequest = (url, json) => {
    return new Promise((resolve, reject) => {
      $.ajax({
        url: url,
        type: "POST",
        data: json,
        contentType: "application/json",
        success: function (data) {
          resolve(data.redirect_url);
        },
        error: function (jqXHR, textStatus, errorThrown) {
          reject({ jqXHR, textStatus, errorThrown });
        },
      });
    });
  };

  const sendDownloadRequest = (url, json) => {
    return new Promise((resolve, reject) => {
      $.ajax({
        url: url,
        type: "POST",
        data: json,
        contentType: "application/json",
        success: function (data, textStatus, request) {
          const contentType = request.getResponseHeader("Content-Type");
          if (contentType === "application/pdf") {
            const contentDisposition = request.getResponseHeader("Content-Disposition");
            const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
            const filename = filenameMatch ? filenameMatch[1] : "demo.pdf";
  
            const blob = new Blob([data], { type: contentType });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            a.remove();
            resolve();
          } else {
            resolve(data.redirect_url);
          }
        },
        error: function (jqXHR, textStatus, errorThrown) {
          reject({ jqXHR, textStatus, errorThrown });
        },
        xhrFields: {
          responseType: "blob", // Set the responseType to handle binary data
        },
      });
    });
  };

  const sendGetRequest = (url) => {
    return new Promise((resolve, reject) => {
      $.ajax({
        url: url,
        type: "GET",
        dataType: 'json',
        success: function (data) {
          resolve(data);
        },
        error: function (jqXHR, textStatus, errorThrown) {
          reject({ jqXHR, textStatus, errorThrown });
        },
      });
    });
  };

  const validateForm = (form, event, callback) => {
    form.classList.add('was-validated');
    if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
        callback(false);
    } else {
        // for (let i = 0; i < form.elements.length; i++) {
        //   const element = form.elements[i];
        //   if (!element.checkValidity()) {
        //     alert(`Invalid field: ${element.name}`);
        //   }
        // }
        // If validation is successful, update button style
        event.preventDefault()
        callback(true);
    }
  };

  function extractRunIds(input) {
    const runIds = [];
    for (const item of input) {
        const runIdMatch = item.match(/'runId':(.*?)(,|$)/);
        if (runIdMatch) {
            runIds.push(runIdMatch[1]);
        }
    }
    return runIds;
  }



  class DomNode {
      constructor(s) {
          this.node = s;
      }
      addClass(s) {
          this.isValidNode() && this.node.classList.add(s);
      }
      removeClass(s) {
          this.isValidNode() && this.node.classList.remove(s);
      }
      toggleClass(s) {
          this.isValidNode() && this.node.classList.toggle(s);
      }
      hasClass(s) {
          this.isValidNode() && this.node.classList.contains(s);
      }
      data(s) {
          if (this.isValidNode())
              try {
                  return JSON.parse(this.node.dataset[this.camelize(s)])
              } catch (t) {
                  return this.node.dataset[this.camelize(s)]
              }
          return null
      }
      attr(s) {
          return this.isValidNode() && this.node[s]
      }
      setAttribute(s, t) {
          this.isValidNode() && this.node.setAttribute(s, t);
      }
      removeAttribute(s) {
          this.isValidNode() && this.node.removeAttribute(s);
      }
      setProp(s, t) {
          this.isValidNode() && (this.node[s] = t);
      }
      on(s, t) {
          this.isValidNode() && this.node.addEventListener(s, t);
      }
      isValidNode() {
          return !!this.node
      }
      camelize(s) {
          const t = s.replace(/[-_\s.]+(.)?/g, ((s,t)=>t ? t.toUpperCase() : ""));
          return `${t.substr(0, 1).toLowerCase()}${t.substr(1)}`
      }
  }

  const elementMap = new Map;
  class BulkSelect {
      constructor(e, t) {
          this.element = e,
          this.option = {
              displayNoneClassName: "d-none",
              ...t
          },
          elementMap.set(this.element, this);
      }
      static getInstance(e) {
          return elementMap.has(e) ? elementMap.get(e) : null
      }
      init() {
          this.attachNodes(),
          this.clickBulkCheckbox(),
          this.clickRowCheckbox();
      }

      getSelectedRows() {
        const selectedRows = Array.from(this.bulkSelectRows).filter((row) => row.checked).map((row) => {
            const checkboxData = getData(row, "bulk-select-row");
            // if (checkboxData.template_id == "no data"){
            //   checkboxData["template_id"] = checkboxData.testName;
            // }
            delete checkboxData.duration;
            delete checkboxData.startTime;
            delete checkboxData.endTime;
            delete checkboxData.maxThreads;
            delete checkboxData.testName;
            return checkboxData;
        });
    
        return selectedRows;
    }
      attachNodes() {
          const {body: e, actions: t, replacedElement: s} = getData(this.element, "bulk-select");
          this.actions = new DomNode(document.getElementById(t)),
          this.replacedElement = new DomNode(document.getElementById(s)),
          this.bulkSelectRows = document.getElementById(e).querySelectorAll("[data-bulk-select-row]");
          
      }
      attachRowNodes(e) {
          this.bulkSelectRows = e;
      }
      clickBulkCheckbox() {
          this.element.addEventListener("click", (()=>{
              if ("indeterminate" === this.element.indeterminate)
                  return this.actions.addClass(this.option.displayNoneClassName),
                  this.replacedElement.removeClass(this.option.displayNoneClassName),
                  this.removeBulkCheck(),
                  void this.bulkSelectRows.forEach((e=>{
                      const t = new DomNode(e);
                      t.checked = !1,
                      t.setAttribute("checked", !1);
                  }
                  ));
              this.toggleDisplay(),
              this.bulkSelectRows.forEach((e=>{
                  e.checked = this.element.checked;
              }
              ));
          }
          ));
      }
      clickRowCheckbox() {
          this.bulkSelectRows.forEach((e=>{
              new DomNode(e).on("click", (()=>{
                  "indeterminate" !== this.element.indeterminate && (this.element.indeterminate = !0,
                  this.element.setAttribute("indeterminate", "indeterminate"),
                  this.element.checked = !0,
                  this.element.setAttribute("checked", !0),
                  this.actions.removeClass(this.option.displayNoneClassName),
                  this.replacedElement.addClass(this.option.displayNoneClassName)),
                  [...this.bulkSelectRows].every((e=>e.checked)) && (this.element.indeterminate = !1,
                  this.element.setAttribute("indeterminate", !1)),
                  [...this.bulkSelectRows].every((e=>!e.checked)) && (this.removeBulkCheck(),
                  this.toggleDisplay());
              }
              ));
          }
          ));
      }
      removeBulkCheck() {
          this.element.indeterminate = !1,
          this.element.removeAttribute("indeterminate"),
          this.element.checked = !1,
          this.element.setAttribute("checked", !1);
      }
      toggleDisplay() {
          this.actions.toggleClass(this.option.displayNoneClassName),
          this.replacedElement.toggleClass(this.option.displayNoneClassName);
      }
  }
  const bulkSelectInit = ()=>{
      const e = document.querySelectorAll("[data-bulk-select]");
      e.length && e.forEach((e=>{
          new BulkSelect(e).init();
      }
      ));
  };

  const togglePaginationButtonDisable = (button, disabled) => {
      button.disabled = disabled;
      button.classList[disabled ? 'add' : 'remove']('disabled');
  };
    
  const listInit = () => {
      const { getData } = window.perforge.utils;
      if (window.List) {
        const lists = document.querySelectorAll('[data-list]');
    
        if (lists.length) {
          lists.forEach(el => {
            const bulkSelect = el.querySelector('[data-bulk-select]');
    
            let options = getData(el, 'list');
    
            if (options.pagination) {
              options = {
                ...options,
                pagination: {
                  item: `<li><button class='page' type='button'></button></li>`,
                  ...options.pagination
                }
              };
            }
    
            const paginationButtonNext = el.querySelector(
              '[data-list-pagination="next"]'
            );
            const paginationButtonPrev = el.querySelector(
              '[data-list-pagination="prev"]'
            );
            const viewAll = el.querySelector('[data-list-view="*"]');
            const viewLess = el.querySelector('[data-list-view="less"]');
            const listInfo = el.querySelector('[data-list-info]');
            const listFilter = document.querySelector('[data-list-filter]');
            const list = new List(el, options);
    
            // -------fallback-----------
    
            list.on('updated', item => {
              const fallback =
                el.querySelector('.fallback') ||
                document.getElementById(options.fallback);
    
              if (fallback) {
                if (item.matchingItems.length === 0) {
                  fallback.classList.remove('d-none');
                } else {
                  fallback.classList.add('d-none');
                }
              }
            });
    
            // ---------------------------------------
    
            const totalItem = list.items.length;
            const itemsPerPage = list.page;
            const btnDropdownClose = list.listContainer.querySelector('.btn-close');
            let pageQuantity = Math.ceil(totalItem / itemsPerPage);
            let numberOfcurrentItems = list.visibleItems.length;
            let pageCount = 1;
    
            btnDropdownClose &&
              btnDropdownClose.addEventListener('search.close', () => {
                list.fuzzySearch('');
              });
    
            const updateListControls = () => {
              listInfo &&
                (listInfo.innerHTML = `${list.i} to ${numberOfcurrentItems} <span> Items of </span>${totalItem}`);
    
              paginationButtonPrev &&
                togglePaginationButtonDisable(
                  paginationButtonPrev,
                  pageCount === 1
                );
              paginationButtonNext &&
                togglePaginationButtonDisable(
                  paginationButtonNext,
                  pageCount === pageQuantity
                );
    
              if (pageCount > 1 && pageCount < pageQuantity) {
                togglePaginationButtonDisable(paginationButtonNext, false);
                togglePaginationButtonDisable(paginationButtonPrev, false);
              }
            };
    
            // List info
            updateListControls();
    
            if (paginationButtonNext) {
              paginationButtonNext.addEventListener('click', e => {
                e.preventDefault();
                pageCount += 1;
    
                const nextInitialIndex = list.i + itemsPerPage;
                nextInitialIndex <= list.size() &&
                  list.show(nextInitialIndex, itemsPerPage);
                numberOfcurrentItems += list.visibleItems.length;
                updateListControls();
              });
            }
    
            if (paginationButtonPrev) {
              paginationButtonPrev.addEventListener('click', e => {
                e.preventDefault();
                pageCount -= 1;
    
                numberOfcurrentItems -= list.visibleItems.length;
                const prevItem = list.i - itemsPerPage;
                prevItem > 0 && list.show(prevItem, itemsPerPage);
                updateListControls();
              });
            }
    
            const toggleViewBtn = () => {
              viewLess.classList.toggle('d-none');
              viewAll.classList.toggle('d-none');
            };
    
            if (viewAll) {
              viewAll.addEventListener('click', () => {
                list.show(1, totalItem);
                pageQuantity = 1;
                pageCount = 1;
                numberOfcurrentItems = totalItem;
                updateListControls();
                toggleViewBtn();
              });
            }
            if (viewLess) {
              viewLess.addEventListener('click', () => {
                list.show(1, itemsPerPage);
                pageQuantity = Math.ceil(totalItem / itemsPerPage);
                pageCount = 1;
                numberOfcurrentItems = list.visibleItems.length;
                updateListControls();
                toggleViewBtn();
              });
            }
            // numbering pagination
            if (options.pagination) {
              el.querySelector('.pagination').addEventListener('click', e => {
                if (e.target.classList[0] === 'page') {
                  const pageNum = Number(e.target.getAttribute('data-i'));
                  if (pageNum) {
                    list.show(
                      itemsPerPage * (pageNum - 1) + 1,
                      numberOfcurrentItems
                    );
                    numberOfcurrentItems =
                      list.visibleItems.length < itemsPerPage
                        ? itemsPerPage * (pageNum - 1) + list.visibleItems.length
                        : itemsPerPage * pageNum;
                    pageCount = pageNum;
                    updateListControls();
                  }
                }
              });
            }
            //filter
            if (options.filter) {
              const { key } = options.filter;
              listFilter.addEventListener('change', e => {
                list.filter(item => {
                  if (e.target.value === '') {
                    return true;
                  }
                  return item
                    .values()
                    [key].toLowerCase()
                    .includes(e.target.value.toLowerCase());
                });
              });
            }
    
            //bulk-select
            if (bulkSelect) {
              const bulkSelectInstance = window.perforge.BulkSelect.getInstance(bulkSelect);
              bulkSelectInstance.attachRowNodes(
                list.items.map(item =>
                  item.elm.querySelector('[data-bulk-select-row]')
                )
              );
    
              bulkSelect.addEventListener('change', () => {
                if (list) {
                  if (bulkSelect.checked) {
                    list.items.forEach(item => {
                      item.elm.querySelector(
                        '[data-bulk-select-row]'
                      ).checked = true;
                    });
                  } else {
                    list.items.forEach(item => {
                      item.elm.querySelector(
                        '[data-bulk-select-row]'
                      ).checked = false;
                    });
                  }
                }
              });
            }
          });
        }
      }
  };

  var utils = {
    listInit: listInit,
    validateForm: validateForm,
    sendPostRequest: sendPostRequest,
    sendGetRequest: sendGetRequest,
    extractRunIds: extractRunIds,
    docReady: docReady,
    camelize: camelize,
    getData: getData,
    hasClass: hasClass,
    addClass: addClass,
    removeClass: removeClass,
    setCookie: setCookie,
    getCookie: getCookie,
    getRandomNumber: getRandomNumber
};

  docReady(bulkSelectInit),
  docReady(listInit),
  docReady(() => {

      //Tests
      const selectedRowsBtn = document.querySelector('[data-selected-rows]');
      const selectedAction = document.getElementById('selectedAction');
      const selectedInfluxdb = document.getElementById('influxdbName');
      const selectedTemplateGroup = document.getElementById('templateGroupName');
      const spinner = document.getElementById("spinner-apply");
      const spinnerText = document.getElementById("spinner-apply-text");
      if (selectedRowsBtn) {
        const bulkSelectEl = document.getElementById('bulk-select-example');
        const bulkSelectInstance = window.perforge.BulkSelect.getInstance(bulkSelectEl);
        selectedRowsBtn.addEventListener('click', () => {

          spinner.style.display = "inline-block";
          spinnerText.style.display = "none";
          const transformedList = bulkSelectInstance.getSelectedRows();
          const selectedRows = {}
          selectedRows["tests"] = transformedList;
          selectedRows["selectedAction"] = selectedAction.value;
          if (selectedTemplateGroup.value !== "Choose template group"){
            selectedRows["templateGroup"] = selectedTemplateGroup.value;
          }
          if (selectedAction.value === "pdf_report"){
            sendDownloadRequest('/generate',JSON.stringify(selectedRows)).finally(function (){
              spinner.style.display = "none";
              spinnerText.style.display = "";
            });
          }else if (selectedAction.value === "delete"){
            selectedRows["influxdbName"] = selectedInfluxdb.value;
            sendPostRequest('/generate',JSON.stringify(selectedRows)).finally(function (){
              spinner.style.display = "none";
              spinnerText.style.display = "";
            });
          }else{
            sendPostRequest('/generate',JSON.stringify(selectedRows)).finally(function (){
              spinner.style.display = "none";
              spinnerText.style.display = "";
            });
          }
        });
      }

      //Graphs
    });
  var perforge = {
      utils: utils,
      BulkSelect: BulkSelect
  };

  return perforge;
}
));