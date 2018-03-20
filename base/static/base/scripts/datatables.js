$(document).ready(function() {
    $.fn.dataTable.moment('DD.MM.YYYY');

    const $table = $('#scores');
    function initTable(paging=true) {
        return $table.DataTable({
            "paging": paging,
            "colReorder": true,
            "language": {
                //"url": "//cdn.datatables.net/plug-ins/9dcbecd42ad/i18n/German.json"
                "sEmptyTable":      "Keine Daten in der Tabelle vorhanden",
                "sInfo":            "_START_ bis _END_ von _TOTAL_ Einträgen",
                "sInfoEmpty":       "0 bis 0 von 0 Einträgen",
                "sInfoFiltered":    "(gefiltert von _MAX_ Einträgen)",
                "sInfoPostFix":     "",
                "sInfoThousands":   ".",
                "sLengthMenu":      "_MENU_ Einträge anzeigen",
                "sLoadingRecords":  "Wird geladen...",
                "sProcessing":      "Bitte warten...",
                "sSearch":          "Suchen",
                "sZeroRecords":     "Keine Einträge vorhanden.",
                "oPaginate": {
                    "sFirst":       "Erste",
                    "sPrevious":    "Zurück",
                    "sNext":        "Nächste",
                    "sLast":        "Letzte"
                },
                "oAria": {
                    "sSortAscending":  ": aktivieren, um Spalte aufsteigend zu sortieren",
                    "sSortDescending": ": aktivieren, um Spalte absteigend zu sortieren"
                },
                select: {
                        rows: {
                        _: '%d Zeilen ausgewählt',
                        0: 'Zum Auswählen auf eine Zeile klicken',
                        1: '1 Zeile ausgewählt'
                        }
                }
            }
        });
    }

    let table = initTable();

    const $buttonRow = $('<div></div>');
    $(".table-responsive").prepend($buttonRow);

    const $paginationToggle = $('<button class="btn btn-secondary mb-2" data-toggle="button"></button>');
    function isPagingActive() {
        return table.init()['bPaginate'];
    }
    function updateToggleText() {
        const newText = isPagingActive() ? "alle anzeigen" : "seitenweise anzeigen";
        $paginationToggle.text(newText);
    }
    updateToggleText();
    $paginationToggle.click(e => {
        table.destroy()
        table = initTable(!isPagingActive());
        updateToggleText();
    });
    $buttonRow.append($paginationToggle);

    const dateColumnIndex = $("thead > tr > th:contains('Datum')", $table).index() - 1;
    /**
      * @param n number of the target dates row, starting with 1 for the first row<br/>
      *          negative n are counted from the end, starting with -1 for the last row
      */
    function nthDateCell(n) {
        if (n < 0) {
            return $(`tbody > tr:nth-last-child(${Math.abs(n)}) > td:eq(${dateColumnIndex})`, $table);
        }
        else {
            return $(`tbody > tr:nth-child(${n}) > td:eq(${dateColumnIndex})`, $table);
        }
    }
    function highlightRow($element) {
        const offset = $element.offset();
        offset.left -= 20;
        offset.top -= 20;
        $('html, body').animate({
            scrollTop: offset.top,
            scrollLeft: offset.left
        });
        $element.parent().addClass("table-info");
    }
    function highlightMostRecentItem(today = moment()) {
        table.order([dateColumnIndex, "asc"]).draw();
        for (let pageIndex = 0; pageIndex < table.page.info().pages; pageIndex++) {
            table.page(pageIndex).draw("page");
            const firstDate = moment(nthDateCell(1).text(), "DD.MM.YYYY");
            if (today < firstDate) {
                if (pageIndex === 0) {
                    // no item in past
                    return;
                }
                else {
                    // last item on previous page is most recent item
                    table.page("previous").draw("page");
                    highlightRow(nthDateCell(-1));
                    return;
                }
            }
            const lastDate = moment(nthDateCell(-1).text(), "DD.MM.YYYY");
            if (today >= lastDate) {
                if (pageIndex  === table.page.info().pages - 1) {
                    // last item on this last page is most recent item
                    highlightRow(nthDateCell(-1));
                    return;
                }
                else {
                    // last item on this page is in past, try next page
                    table.page("next").draw("page");
                    continue;
                }
            }
            // rowNumber starting from 2 (start with secon row)
            for (let rowNumber = 2; rowNumber < table.page.info().length - 1; rowNumber++) {
                const date = moment(nthDateCell(rowNumber).text(), "DD.MM.YYYY");
                if (today < date) {
                    // last item is the most recent item
                    highlightRow(nthDateCell(rowNumber - 1));
                    return;
                }
            }
        }
    }
    if (dateColumnIndex >= 0) {
        const $btnToday = $('<button class="btn btn-secondary mb-2 ml-2">heute <i class="fa fa-arrow-down"></i></button>');
        const query = `tbody > tr > td:eq(${dateColumnIndex})`;
        $btnToday.click(e => highlightMostRecentItem());
        $buttonRow.append($btnToday);
    }

} );
