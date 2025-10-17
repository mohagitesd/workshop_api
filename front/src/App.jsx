import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Favorites from "./pages/Favorites";
import MuseumDetail from "./pages/MuseumDetail";
import Login from "./pages/Login";
import Header from "./components/Header";


function App() {
  return (
    <Router>
      <Header />
      <main className="site-main">
        <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/favorites" element={<Favorites />} />
            <Route path="/museum/:id" element={<MuseumDetail />} />
            <Route path="/login" element={<Login />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
