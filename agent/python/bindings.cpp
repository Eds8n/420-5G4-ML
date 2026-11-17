// Exposition pybind11 de la logique C++ (Book, User, Library) a Python.
//
// Regle de securite memoire : la classe Library possede ses objets via
// std::vector<std::unique_ptr<...>> et ses methodes renvoient des POINTEURS
// BRUTS (Book*, User*, vector<Book*>). Si on les exposait tels quels,
// pybind11 prendrait par defaut la propriete de ces pointeurs
// (return_value_policy::take_ownership) et Python finirait par supprimer des
// objets encore possedes par Library -> double free / pointeurs invalides.
//
// On ne fait donc JAMAIS traverser un pointeur brut vers Python : les
// fonctions ci-dessous renvoient des COPIES (types valeur). Python ne peut
// muter la bibliotheque que via les methodes de Library.

#include <optional>
#include <string>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>  // conversions std::vector<...> et std::optional<...>

#include "book.h"
#include "filemanager.h"
#include "library.h"
#include "user.h"

namespace py = pybind11;

// ---------------------------------------------------------------------------
// Wrappers par copie : transforment les pointeurs bruts en valeurs.
// ---------------------------------------------------------------------------

std::vector<Book> copy_books(const std::vector<Book*>& books) {
    std::vector<Book> copies;
    copies.reserve(books.size());
    for (const Book* book : books) {
        copies.push_back(*book);
    }
    return copies;
}

std::vector<User> copy_users(const std::vector<User*>& users) {
    std::vector<User> copies;
    copies.reserve(users.size());
    for (const User* user : users) {
        copies.push_back(*user);
    }
    return copies;
}

std::optional<Book> find_book_by_isbn(Library& library, const std::string& isbn) {
    if (Book* book = library.findBookByISBN(isbn)) {
        return *book;
    }
    return std::nullopt;
}

std::optional<User> find_user_by_id(Library& library, const std::string& userId) {
    if (User* user = library.findUserById(userId)) {
        return *user;
    }
    return std::nullopt;
}

// ---------------------------------------------------------------------------
// Module Python
// ---------------------------------------------------------------------------

PYBIND11_MODULE(bibliotheque_core, m) {
    m.doc() = "Logique C++ du projet bibliotheque exposee a Python (pybind11)";

    // --- Book (type valeur, lecture seule cote Python) ---
    py::class_<Book>(m, "Book")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&, const std::string&>(),
             py::arg("title"), py::arg("author"), py::arg("isbn"))
        .def_property_readonly("title", &Book::getTitle)
        .def_property_readonly("author", &Book::getAuthor)
        .def_property_readonly("isbn", &Book::getISBN)
        .def_property_readonly("available", &Book::getAvailability)
        .def_property_readonly("borrower_id", &Book::getBorrowerId)
        .def("__repr__", [](const Book& book) {
            return "<Book " + book.getTitle() + " (" + book.getISBN() + ")>";
        })
        .def("__str__", &Book::toString);

    // --- User (type valeur, lecture seule cote Python) ---
    py::class_<User>(m, "User")
        .def(py::init<>())
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("name"), py::arg("user_id"))
        .def_property_readonly("name", &User::getName)
        .def_property_readonly("user_id", &User::getUserId)
        .def_property_readonly("borrowed_books", &User::getBorrowedBooks)
        .def("number_of_borrowed_books", &User::getNumberOfBorrowedBooks)
        .def("__repr__", [](const User& user) {
            return "<User " + user.getName() + " (" + user.getUserId() + ")>";
        })
        .def("__str__", &User::toString);

    // --- Library ---
    py::class_<Library>(m, "Library")
        .def(py::init<>())

        // Livres
        .def("add_book", &Library::addBook, py::arg("book"))
        .def("remove_book", &Library::removeBook, py::arg("isbn"))
        .def("find_book_by_isbn", &find_book_by_isbn, py::arg("isbn"))
        .def("search_books_by_title",
             [](Library& library, const std::string& title) {
                 return copy_books(library.searchBooksByTitle(title));
             },
             py::arg("title"))
        .def("search_books_by_author",
             [](Library& library, const std::string& author) {
                 return copy_books(library.searchBooksByAuthor(author));
             },
             py::arg("author"))
        .def("get_all_books",
             [](Library& library) { return copy_books(library.getAllBooks()); })
        .def("get_available_books",
             [](Library& library) { return copy_books(library.getAvailableBooks()); })

        // Utilisateurs
        .def("add_user", &Library::addUser, py::arg("user"))
        .def("find_user_by_id", &find_user_by_id, py::arg("user_id"))
        .def("get_all_users",
             [](Library& library) { return copy_users(library.getAllUsers()); })

        // Emprunts
        .def("check_out_book", &Library::checkOutBook,
             py::arg("isbn"), py::arg("user_id"))
        .def("return_book", &Library::returnBook, py::arg("isbn"))

        // Statistiques
        .def("get_total_books", &Library::getTotalBooks)
        .def("get_available_book_count", &Library::getAvailableBookCount)
        .def("get_checked_out_book_count", &Library::getCheckedOutBookCount);

    // --- FileManager (persistance : lecture/ecriture de books.txt et users.txt) ---
    // FileManager ne possede rien : il lit/ecrit des fichiers pour une Library
    // passee en argument, donc aucun probleme de propriete memoire ici.
    py::class_<FileManager>(m, "FileManager")
        .def(py::init<const std::string&, const std::string&>(),
             py::arg("books_file"), py::arg("users_file"))
        .def("save_library_data", &FileManager::saveLibraryData, py::arg("library"))
        .def("load_library_data", &FileManager::loadLibraryData, py::arg("library"))
        .def("save_books_to_file", &FileManager::saveBooksToFile, py::arg("library"))
        .def("save_users_to_file", &FileManager::saveUsersToFile, py::arg("library"))
        .def("load_books_from_file", &FileManager::loadBooksFromFile, py::arg("library"))
        .def("load_users_from_file", &FileManager::loadUsersFromFile, py::arg("library"))
        .def("file_exists", &FileManager::fileExists, py::arg("filename"))
        .def("create_backup", &FileManager::createBackup);
}
