import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Table from "./pages/Table";
import Fixtures from "./pages/Fixtures";

function App() {
    return (
        <>
            <BrowserRouter>
                <Routes>
                    <Route index element={<Home />} />
                    <Route path="/home" element={<Home />} />
                    <Route path="/premier-league" element={<Table />} />
                    <Route path="/premier-league/teams" element={<Table />} />
                    <Route
                        path="/premier-league/fixtures"
                        element={<Fixtures />}
                    />
                    <Route path="*" element={<h1>404 Not Found</h1>} />
                </Routes>
            </BrowserRouter>
        </>
    );
}

export default App;
