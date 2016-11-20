use std::collections::hash_set::HashSet;
use std::time::Instant;
use std::env;

fn main() {
    let limit = env::args().nth(1).unwrap().parse::<u32>().unwrap();

    let mut one = HashSet::new();
    let start = Instant::now();
    for i in 1..limit {
        one.insert(i);
    }

    let mid = Instant::now();

    let mut two = HashSet::new();
    for v in one {
        two.insert(v);
    }

    let end = Instant::now();

    let time_a =  mid.duration_since(start);
    let time_b =  end.duration_since(mid);
    println!("{}.{},{}.{}",
             time_a.as_secs(), time_a.subsec_nanos()/1000000,
             time_b.as_secs(), time_b.subsec_nanos()/1000000,
    )
}
