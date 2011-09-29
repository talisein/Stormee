#include <iostream>
#include <gtkmm/imagemenuitem.h>
#include <gtkmm/filechooserdialog.h>
#include <gtkmm/linkbutton.h>
#include <gtkmm.h>
#include "main_window.h"
#include "util.h"
#include "capreader.hxx"

CAPViewer::KeyTable::KeyTable(BaseObjectType* cobject, const Glib::RefPtr<Gtk::Builder>&) : Gtk::Grid(cobject), rows(1), columns(2)
{
  Gtk::Label *label = manage(new Gtk::Label("No CAP file loaded.", 0.0, 0.5));
  attach(*label, 0, 0, 1, 1);

  set_row_homogeneous(false);
  set_column_homogeneous(false);
  set_row_spacing(4);
  show_all();
}

CAPViewer::KeyTable::~KeyTable() {
}

void CAPViewer::KeyTable::add(const Glib::ustring& key, const Glib::ustring& value, const Glib::ustring& keyTooltip, const Glib::ustring& valueTooltip, const Glib::ustring& url)
{
  Gtk::LinkButton *valueTag = manage(new Gtk::LinkButton(url, value));

  valueTag->set_relief(Gtk::RELIEF_NONE);
  valueTag->set_label(value);
  
  add_widget(key, valueTag, keyTooltip, valueTooltip);
}

void CAPViewer::KeyTable::add(const Glib::ustring& key, const Glib::ustring& value, const Glib::ustring& keyTooltip, const Glib::ustring& valueTooltip)
{
  Gtk::Label *valueTag = manage(new Gtk::Label(value, 0.0, 0.5));

  valueTag->set_single_line_mode(true);
  valueTag->set_ellipsize(Pango::EllipsizeMode::ELLIPSIZE_END);

  add_widget(key, valueTag, keyTooltip, valueTooltip);
}

void CAPViewer::KeyTable::clear() {
  for ( auto pWidget : get_children() ) {
    remove(*pWidget);
    delete pWidget;
  }
}

void CAPViewer::KeyTable::add_widget(const Glib::ustring& key, Gtk::Widget* const valueTag, const Glib::ustring& keyTooltip, const Glib::ustring& valueTooltip) {
  Gtk::Label *keyTag = manage(new Gtk::Label(key, 0.0, 0.5));

  keyTag->set_single_line_mode(true);
  keyTag->set_tooltip_text(keyTooltip);
  valueTag->set_tooltip_text(valueTooltip);
  valueTag->set_sensitive(true);

  rows += 1;
  attach(*keyTag, 0, rows-1, 1, 1);
  attach(*valueTag, 1, rows-1, 1, 1);
  show_all();
}


CAPViewer::Window::Window(BaseObjectType* cobject, const Glib::RefPtr<Gtk::Builder>& refBuilder) : Gtk::Window(cobject)
{

  Gtk::ImageMenuItem* openFileItem = 0;
  signal_cap.connect(sigc::mem_fun(*this, &CAPViewer::Window::consume_cap));

  refBuilder->get_widget("openFileMenuItem", openFileItem);
  if (openFileItem) {
    openFileItem->signal_activate().connect( sigc::mem_fun(this, &CAPViewer::Window::on_openFileMenu ));
  }

  refBuilder->get_widget("keyValueTreeView", keyValueTreeView);
  m_refKeyValueModel = Gtk::TreeStore::create(m_TreeViewModelColumns);
  keyValueTreeView->set_model(m_refKeyValueModel);
  keyColumn.pack_start(m_TreeViewModelColumns.m_col_key);
  valueColumn.pack_start(m_TreeViewModelColumns.m_col_value);
  keyColumn.set_expand(false);
  keyColumn.set_alignment(1.0);
  valueColumn.set_expand(true);
  
  keyValueTreeView->append_column(keyColumn);
  keyValueTreeView->append_column(valueColumn);
  keyValueTreeView->set_has_tooltip(true);
  keyValueTreeView->signal_query_tooltip().connect( sigc::mem_fun(this, &CAPViewer::Window::m_query_tooltip ));

  auto iter = m_refKeyValueModel->append();
  (*iter)[m_TreeViewModelColumns.m_col_value] = "No CAP File Loaded";

  refBuilder->get_widget("comboBox2", m_comboBox);
  m_refComboBoxModel = Gtk::TreeStore::create(m_ComboBoxModelColumns);
  m_comboBox->set_model(m_refComboBoxModel);
  m_comboBox->pack_start(m_ComboBoxModelColumns.m_col_title);
  m_comboBox->pack_start(m_ComboBoxModelColumns.m_col_status);
  m_comboBox->pack_start(m_ComboBoxModelColumns.m_col_msgType);
  m_comboBox->pack_start(m_ComboBoxModelColumns.m_col_urgency);
  m_comboBox->pack_start(m_ComboBoxModelColumns.m_col_severity);
  m_comboBox->signal_changed()
    .connect(sigc::mem_fun(*this, &CAPViewer::Window::on_combo_changed));

  show_all_children();
}

bool CAPViewer::Window::m_query_tooltip(int x, int y, bool, const Glib::RefPtr<Gtk::Tooltip>& tooltip) {
  int nx, ny, cellx, celly;
  Gtk::TreeModel::Path path;
  Gtk::TreeView::Column* column;

  keyValueTreeView->convert_widget_to_bin_window_coords(x, y, nx, ny);
  bool isRow = keyValueTreeView->get_path_at_pos(nx, ny, path, column, cellx, celly);
  if (!isRow) // Cursor is not hovering over a row
    return false;

  keyValueTreeView->set_tooltip_cell(tooltip, &path, column, 0);
  auto iter = m_refKeyValueModel->get_iter(path);
  if (iter) {
    if ( column == &keyColumn ) {
      Glib::ustring text = (*iter)[m_TreeViewModelColumns.m_col_keytip];
      if ( text.length() > 0 ) {
	tooltip->set_text(text);
	return true;
      } else {
	return false;
      }
    } 

    if ( column == &valueColumn ) {
      Glib::ustring text = (*iter)[m_TreeViewModelColumns.m_col_valuetip];
      if ( text.length() > 0 ) {
	tooltip->set_text(text);
	return true;
      } else {
	return false; 
      }
    }

    return false;

  } else {
    return false;
  }
}

void CAPViewer::Window::on_combo_changed() {
  auto iter = m_comboBox->get_active();
  if (iter) {
    Gtk::TreeModel::Row row = *iter;
    if (row) {
      CAPViewer::CAP cap = row[m_ComboBoxModelColumns.m_col_cap];
      //      keyValueTable->clear();
      m_refKeyValueModel->clear();

      addKeyValue("Note", cap.getNote(), CAPViewer::CAP::aboutNote());
      addKeyValue("Message Type", CAPViewer::msgTypeStringMap.find(cap.getMsgType())->second, CAPViewer::aboutMsgType(), CAPViewer::aboutMsgType(cap.getMsgType()));
      addKeyValue("Incidents", cap.getIncidents(), CAPViewer::CAP::aboutIncidents());
      addKeyValue("Status", CAPViewer::statusStringMap.find(cap.getStatus())->second, CAPViewer::aboutStatus(), CAPViewer::aboutStatus(cap.getStatus()));
      addKeyValue("Scope", CAPViewer::scopeStringMap.find(cap.getScope())->second, CAPViewer::aboutScope(), CAPViewer::aboutScope(cap.getScope()));
      addKeyValue("Addresses", cap.getAddresses(), CAPViewer::CAP::aboutAddresses());
      addKeyValue("Restriction", cap.getRestriction(), CAPViewer::CAP::aboutRestriction());
      addKeyValue("Source", cap.getSource(), CAPViewer::CAP::aboutSource());

    }
  }
}

void CAPViewer::Window::addKeyValue(const Glib::ustring& key, const Glib::ustring& value, const Glib::ustring& keyTooltip, const Glib::ustring& valueTooltip) {
  if (value.length() > 0) {
    //    keyValueTable->add(key, value, keyTooltip, valueTooltip);
    auto iter = m_refKeyValueModel->append();
    (*iter)[m_TreeViewModelColumns.m_col_key] = key;
    (*iter)[m_TreeViewModelColumns.m_col_value] = value;
    (*iter)[m_TreeViewModelColumns.m_col_keytip] = keyTooltip;
    if (valueTooltip.length() > 0)
      (*iter)[m_TreeViewModelColumns.m_col_valuetip] = valueTooltip;
  }
}

CAPViewer::Window::~Window() {
}

void CAPViewer::Window::on_button_quit() {
  hide();
}

void CAPViewer::Window::consume_cap() {
  Glib::Mutex::Lock lock(mutex);
  
  while ( !queue_cap.empty() ) {
    CAPViewer::CAP cap = queue_cap.front(); queue_cap.pop();
    if ( seen_caps.count(cap) < 1 ) {
      seen_caps.insert(cap);
      // populate
      Gtk::TreeModel::Row row = *(m_refComboBoxModel->append());
      row[m_ComboBoxModelColumns.m_col_title] = cap.getTitle();
      row[m_ComboBoxModelColumns.m_col_status] = CAPViewer::statusStringMap.find(cap.getStatus())->second;
      row[m_ComboBoxModelColumns.m_col_msgType] = CAPViewer::msgTypeStringMap.find(cap.getMsgType())->second;
      row[m_ComboBoxModelColumns.m_col_urgency] = CAPViewer::urgencyStringMap.find(cap.getUrgency())->second;
      row[m_ComboBoxModelColumns.m_col_severity] = CAPViewer::severityStringMap.find(cap.getSeverity())->second;
      row[m_ComboBoxModelColumns.m_col_cap] = cap;
    }
  }
}

void CAPViewer::Window::produce_cap_from_file(Glib::RefPtr<Gio::File> fptr) {
  CAPViewer::CAPReaderFile reader(fptr);
  reader.do_parse();
  
  {
    for ( auto capptr : reader.getCAPs() ) {
      Glib::Mutex::Lock lock(mutex);
      queue_cap.push(*capptr);
    }
  }
  
  signal_cap();
}

void CAPViewer::Window::on_openFileMenu() {
  Gtk::FileChooserDialog fcd("Please choose a CAP file", Gtk::FILE_CHOOSER_ACTION_OPEN);
  
  fcd.set_transient_for(*this);
  fcd.add_button(Gtk::Stock::CANCEL, Gtk::RESPONSE_CANCEL);
  fcd.add_button(Gtk::Stock::OPEN, Gtk::RESPONSE_OK);

  fcd.set_select_multiple(true);
  int result = fcd.run();

  switch (result) {
  case Gtk::RESPONSE_OK:
    
    for (auto fptr : fcd.get_files() ) {
      Glib::Thread::create(sigc::bind(sigc::mem_fun(*this, &CAPViewer::Window::produce_cap_from_file),fptr), false);
    }
    
    break;
  case Gtk::RESPONSE_CANCEL:
    break;
  default:
    break;
  }
}
