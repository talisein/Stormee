#include <set>
#include <queue>
#include <gtkmm/window.h>
#include <gtkmm/scrolledwindow.h>
#include <gtkmm/widget.h>
#include <gtkmm/grid.h>
#include <gtkmm/builder.h>
#include <gtkmm/treestore.h>
#include <gtkmm/combobox.h>
#include <gtkmm/tooltip.h>
#include <gtkmm/notebook.h>
#include <gtkmm/texttagtable.h>
#include <gtkmm/textbuffer.h>
#include <glibmm/thread.h>
#include <giomm/file.h>

#include "cap.hxx"
#include "xmpp.hxx"

namespace CAPViewer {
  
  class Window : public Gtk::Window {
  public:
    Window(BaseObjectType* cobject, const Glib::RefPtr<Gtk::Builder>& refGlade);
    ~Window();
    
    void accept_caps(const std::vector<std::shared_ptr<CAPViewer::CAP>>&);

  protected:
    void on_button_quit();
    void on_openFileMenu();
    
    class ComboBoxModelColumns : public Gtk::TreeModel::ColumnRecord {
    public:
      
      ComboBoxModelColumns() 
	{ add(m_col_title); add(m_col_status); 
	  add(m_col_msgType); add(m_col_urgency); 
	  add(m_col_severity); add(m_col_cap); }
      
      Gtk::TreeModelColumn<Glib::ustring> m_col_title;
      Gtk::TreeModelColumn<Glib::ustring> m_col_status;
      Gtk::TreeModelColumn<Glib::ustring> m_col_msgType;
      Gtk::TreeModelColumn<Glib::ustring> m_col_urgency;
      Gtk::TreeModelColumn<Glib::ustring> m_col_severity;
      Gtk::TreeModelColumn<CAPViewer::CAP> m_col_cap;
    } m_ComboBoxModelColumns;

    class TreeViewModelColumns : public Gtk::TreeModel::ColumnRecord {
    public:
      TreeViewModelColumns()
	{ add(m_col_key); add(m_col_value); 
	  add(m_col_keytip); add(m_col_valuetip); }

       Gtk::TreeModelColumn<Glib::ustring> m_col_key;
       Gtk::TreeModelColumn<Glib::ustring> m_col_value;
       Gtk::TreeModelColumn<Glib::ustring> m_col_keytip;
       Gtk::TreeModelColumn<Glib::ustring> m_col_valuetip;
       
    } m_TreeViewModelColumns;

    Gtk::TreeView::Column keyColumn;
    Gtk::TreeView::Column valueColumn;

  private:
    void produce_cap_from_file(Glib::RefPtr<Gio::File>);
    void produce_cap_from_url(const Glib::ustring&);
    void consume_cap();
    void on_combo_changed();
    void addKeyValue(const Glib::ustring&, const Glib::ustring&, const Glib::ustring& = "", const Glib::ustring& valueTooltip = "");
    void addKeyValueChild(const Gtk::TreeNodeChildren&, const Glib::ustring&, const Glib::ustring&, const Glib::ustring& keyTooltip = "", const Glib::ustring& valueTooltip = "");
    bool m_query_tooltip(int x, int y, bool keyboard_tooltip, const Glib::RefPtr<Gtk::Tooltip>& tooltip);

    std::shared_ptr<CAPViewer::XmppClient> xmppClient;
    Glib::Thread* xmppThreadPtr;
    sigc::connection xmppConnection;

    std::set<CAPViewer::CAP> seen_caps;
    std::queue<CAPViewer::CAP> queue_cap;
    Glib::Mutex mutex;
    Glib::Dispatcher signal_cap;

    Glib::RefPtr<Gtk::TreeStore> m_refComboBoxModel;
    Glib::RefPtr<Gtk::TreeStore> m_refKeyValueModel;
    Gtk::ComboBox* m_comboBox;
    Gtk::TreeView* keyValueTreeView;
    Gtk::Notebook* m_notebook;
    Glib::RefPtr<Gtk::TextTagTable> tagtable;
    Glib::RefPtr<Gtk::TextBuffer::Tag> centerMonoTag;
    Glib::RefPtr<Gtk::TextBuffer::Tag> leftTag;
    Glib::RefPtr<Gtk::TextBuffer::Tag> leftMonoTag;

  };


  
}







