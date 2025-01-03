export async function editableTable(divid, options) {
  let default_options = {
    data: [{}], //load row data from array
    clipboard: true,
    clipboardPasteAction: "update",
    minHeight: 100,
    autoResize: false, // Resize observer errors abound if this is true!!!
    layout: "fitData", //fit columns to width of table
    responsiveLayout: false, //hide columns that dont fit on the table
    history: true, //allow undo and redo actions on the table
    tooltipsHeader: true,
    footerElement: `<div class="tabulator-footer"></div>`, //add a custom button to the footer element
    columns: [],
  };

  let merged_options = Object.assign(default_options, options);

  let {
    Tabulator,
    EditModule,
    FormatModule,
    HistoryModule,
    InteractionModule,
    MenuModule,
    ResizeColumnsModule,
    SelectRowModule,
    SortModule,
  } = await import("tabulator-tables");
  Tabulator.registerModule([
    Tabulator,
    EditModule,
    FormatModule,
    HistoryModule,
    InteractionModule,
    MenuModule,
    ResizeColumnsModule,
    SelectRowModule,
    SortModule,
  ]);
  return new Tabulator(divid, merged_options);
}
