import Header from "./components/Header";
import NavBar from "./components/NavBar";
import Footer from "./components/Footer";

function App() {
    return (
        <>
            <header className="header-top">
                <Header />
                <NavBar />
            </header>
            <body>Body Section</body>
            <footer>
                <Footer />
            </footer>
        </>
    );
}

export default App;
