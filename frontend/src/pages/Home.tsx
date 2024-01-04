import Header from "../components/Header";
import Footer from "../components/Footer";
import NavBar from "../components/NavBar";

const Home = () => {
    return (
        <>
            <header className="header-top">
                <Header />
                <NavBar />
            </header>
            <body>
                <h1>Landing Page</h1>
            </body>
            <footer>
                <Footer />
            </footer>
        </>
    );
};

export default Home;
