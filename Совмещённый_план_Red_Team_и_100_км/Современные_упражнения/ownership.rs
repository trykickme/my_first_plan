fn main() {
    let first = String::from("local training note");
    let second = first;
    println!("{}", second);
    // Negative compiler case: uncomment the next line to inspect use after move.
    // println!("{}", first);
}
