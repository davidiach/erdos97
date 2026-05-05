// Fast exact search for cyclic orders avoiding two-inequality Kalmanson
// inverse-pair certificates.
//
// This is a dependency-free Rust accelerator for
// scripts/check_kalmanson_two_order_search.py. It intentionally mirrors the
// Python search predicate and uses the C13 replay counters as an equivalence
// guard. The result is still scoped to one fixed selected-witness pattern; it
// is not a proof of Erdos Problem #97.

use std::collections::HashMap;
use std::env;
use std::process;
use std::time::Instant;

type SparseVector = Vec<(usize, i16)>;

#[derive(Debug)]
struct Args {
    name: String,
    n: usize,
    offsets: Vec<isize>,
    prefix: Vec<usize>,
    node_limit: Option<u64>,
    json: bool,
    assert_obstructed: bool,
    assert_c13_expected: bool,
}

#[derive(Debug)]
struct SearchPayload {
    name: String,
    n: usize,
    offsets: Vec<isize>,
    node_limit: Option<u64>,
    prefix: Vec<usize>,
    prefix_valid: bool,
    nodes_visited: u64,
    pruned_branches: u64,
    max_surviving_prefix: Vec<usize>,
    survivor_order: Option<Vec<usize>>,
    status: String,
    trust: String,
    elapsed_seconds: f64,
}

struct Dsu {
    parent: Vec<usize>,
}

impl Dsu {
    fn new(size: usize) -> Self {
        Self {
            parent: (0..size).collect(),
        }
    }

    fn find(&mut self, item: usize) -> usize {
        let parent = self.parent[item];
        if parent != item {
            let root = self.find(parent);
            self.parent[item] = root;
        }
        self.parent[item]
    }

    fn union(&mut self, a: usize, b: usize) {
        let root_a = self.find(a);
        let root_b = self.find(b);
        if root_a != root_b {
            self.parent[root_b] = root_a;
        }
    }
}

struct SearchContext {
    n: usize,
    quad_ids: Vec<[usize; 2]>,
    inverse_id: Vec<Option<usize>>,
    counts: Vec<u16>,
    local_mark: Vec<u32>,
    stamp: u32,
    nodes_visited: u64,
    pruned_branches: u64,
    max_surviving_prefix: Vec<usize>,
    survivor_order: Option<Vec<usize>>,
    stopped_by_limit: bool,
    node_limit: Option<u64>,
}

fn fail(message: &str) -> ! {
    eprintln!("{message}");
    process::exit(2);
}

fn pair_id(n: usize, a: usize, b: usize) -> usize {
    if a == b {
        fail("degenerate pair");
    }
    let (u, v) = if a < b { (a, b) } else { (b, a) };
    u * n + v
}

fn parse_offsets(raw: &str) -> Vec<isize> {
    let mut out = Vec::new();
    for item in raw.split(',') {
        let item = item.trim();
        if item.is_empty() {
            continue;
        }
        match item.parse::<isize>() {
            Ok(value) => out.push(value),
            Err(_) => fail(&format!("invalid offset: {item}")),
        }
    }
    if out.is_empty() {
        fail("--offsets must contain at least one integer");
    }
    out
}

fn parse_prefix(raw: &str) -> Vec<usize> {
    let mut out = Vec::new();
    for item in raw.split(',') {
        let item = item.trim();
        if item.is_empty() {
            continue;
        }
        match item.parse::<usize>() {
            Ok(value) => out.push(value),
            Err(_) => fail(&format!("invalid prefix label: {item}")),
        }
    }
    out
}

fn parse_args() -> Args {
    let mut name: Option<String> = None;
    let mut n: Option<usize> = None;
    let mut offsets: Option<Vec<isize>> = None;
    let mut prefix: Vec<usize> = Vec::new();
    let mut node_limit: Option<u64> = None;
    let mut json = false;
    let mut assert_obstructed = false;
    let mut assert_c13_expected = false;

    let mut iter = env::args().skip(1);
    while let Some(arg) = iter.next() {
        match arg.as_str() {
            "--name" => name = iter.next(),
            "--n" => {
                let raw = iter.next().unwrap_or_else(|| fail("--n requires a value"));
                n = Some(raw.parse().unwrap_or_else(|_| fail("invalid --n")));
            }
            "--offsets" => {
                let raw = iter
                    .next()
                    .unwrap_or_else(|| fail("--offsets requires a value"));
                offsets = Some(parse_offsets(&raw));
            }
            "--prefix" => {
                let raw = iter
                    .next()
                    .unwrap_or_else(|| fail("--prefix requires a value"));
                prefix = parse_prefix(&raw);
            }
            "--node-limit" => {
                let raw = iter
                    .next()
                    .unwrap_or_else(|| fail("--node-limit requires a value"));
                let value = raw
                    .parse::<u64>()
                    .unwrap_or_else(|_| fail("invalid --node-limit"));
                if value == 0 {
                    fail("--node-limit must be positive");
                }
                node_limit = Some(value);
            }
            "--json" => json = true,
            "--assert-obstructed" => assert_obstructed = true,
            "--assert-c13-expected" => assert_c13_expected = true,
            "--help" | "-h" => {
                println!(
                    "Usage: check_kalmanson_two_order_search_fast --name NAME --n N --offsets A,B,C,D [--prefix 0,...] [--node-limit N] [--json]"
                );
                process::exit(0);
            }
            _ => fail(&format!("unknown argument: {arg}")),
        }
    }

    Args {
        name: name.unwrap_or_else(|| fail("--name is required")),
        n: n.unwrap_or_else(|| fail("--n is required")),
        offsets: offsets.unwrap_or_else(|| fail("--offsets is required")),
        prefix,
        node_limit,
        json,
        assert_obstructed,
        assert_c13_expected,
    }
}

fn row_witnesses(n: usize, offsets: &[isize], center: usize) -> Vec<usize> {
    let mut row: Vec<usize> = offsets
        .iter()
        .map(|offset| {
            let value = center as isize + *offset;
            value.rem_euclid(n as isize) as usize
        })
        .collect();
    row.sort_unstable();
    row
}

fn build_distance_classes(n: usize, offsets: &[isize]) -> Vec<usize> {
    let mut dsu = Dsu::new(n * n);
    for center in 0..n {
        let witnesses = row_witnesses(n, offsets, center);
        if witnesses.len() != 4 || witnesses.windows(2).any(|w| w[0] == w[1]) {
            fail(&format!("bad witness row {center}: {witnesses:?}"));
        }
        if witnesses.contains(&center) {
            fail(&format!(
                "witness row contains center {center}: {witnesses:?}"
            ));
        }
        let base = pair_id(n, center, witnesses[0]);
        for witness in witnesses.iter().skip(1) {
            let other = pair_id(n, center, *witness);
            dsu.union(base, other);
        }
    }

    let mut root_to_class: HashMap<usize, usize> = HashMap::new();
    let mut classes = vec![usize::MAX; n * n];
    for a in 0..n {
        for b in (a + 1)..n {
            let id = pair_id(n, a, b);
            let root = dsu.find(id);
            let next_class = root_to_class.len();
            let class = *root_to_class.entry(root).or_insert(next_class);
            classes[id] = class;
            classes[pair_id(n, b, a)] = class;
        }
    }
    classes
}

fn add_term(acc: &mut Vec<(usize, i16)>, class_id: usize, coeff: i16) {
    for item in acc.iter_mut() {
        if item.0 == class_id {
            item.1 += coeff;
            return;
        }
    }
    acc.push((class_id, coeff));
}

fn sparse_vector(classes: &[usize], n: usize, kind: usize, quad: [usize; 4]) -> SparseVector {
    let [a, b, c, d] = quad;
    let mut acc: Vec<(usize, i16)> = Vec::with_capacity(4);
    let diag_ac = classes[pair_id(n, a, c)];
    let diag_bd = classes[pair_id(n, b, d)];
    add_term(&mut acc, diag_ac, 1);
    add_term(&mut acc, diag_bd, 1);
    if kind == 0 {
        add_term(&mut acc, classes[pair_id(n, a, b)], -1);
        add_term(&mut acc, classes[pair_id(n, c, d)], -1);
    } else {
        add_term(&mut acc, classes[pair_id(n, a, d)], -1);
        add_term(&mut acc, classes[pair_id(n, b, c)], -1);
    }
    acc.retain(|item| item.1 != 0);
    acc.sort_unstable_by_key(|item| item.0);
    acc
}

fn negative_vector(vector: &SparseVector) -> SparseVector {
    vector.iter().map(|(idx, value)| (*idx, -*value)).collect()
}

fn get_vector_id(
    vector: SparseVector,
    vector_to_id: &mut HashMap<SparseVector, usize>,
    inverse_id: &mut Vec<Option<usize>>,
) -> usize {
    if let Some(existing) = vector_to_id.get(&vector) {
        return *existing;
    }
    let vector_id = vector_to_id.len();
    let negative = negative_vector(&vector);
    vector_to_id.insert(vector, vector_id);
    inverse_id.push(None);
    if let Some(negative_id) = vector_to_id.get(&negative) {
        inverse_id[vector_id] = Some(*negative_id);
        inverse_id[*negative_id] = Some(vector_id);
    }
    vector_id
}

fn prepare_vector_tables(n: usize, offsets: &[isize]) -> (Vec<[usize; 2]>, Vec<Option<usize>>) {
    let classes = build_distance_classes(n, offsets);
    let mut vector_to_id: HashMap<SparseVector, usize> = HashMap::new();
    let mut inverse_id: Vec<Option<usize>> = Vec::new();
    let mut quad_ids = vec![[usize::MAX; 2]; n * n * n * n];

    for a in 0..n {
        for b in 0..n {
            if b == a {
                continue;
            }
            for c in 0..n {
                if c == a || c == b {
                    continue;
                }
                for d in 0..n {
                    if d == a || d == b || d == c {
                        continue;
                    }
                    let quad = [a, b, c, d];
                    let id0 = get_vector_id(
                        sparse_vector(&classes, n, 0, quad),
                        &mut vector_to_id,
                        &mut inverse_id,
                    );
                    let id1 = get_vector_id(
                        sparse_vector(&classes, n, 1, quad),
                        &mut vector_to_id,
                        &mut inverse_id,
                    );
                    let idx = (((a * n + b) * n + c) * n) + d;
                    quad_ids[idx] = [id0, id1];
                }
            }
        }
    }

    (quad_ids, inverse_id)
}

impl SearchContext {
    fn new(n: usize, offsets: &[isize], node_limit: Option<u64>) -> Self {
        let (quad_ids, inverse_id) = prepare_vector_tables(n, offsets);
        let vector_count = inverse_id.len();
        Self {
            n,
            quad_ids,
            inverse_id,
            counts: vec![0; vector_count],
            local_mark: vec![0; vector_count],
            stamp: 0,
            nodes_visited: 0,
            pruned_branches: 0,
            max_surviving_prefix: Vec::new(),
            survivor_order: None,
            stopped_by_limit: false,
            node_limit,
        }
    }

    fn quad_index(&self, a: usize, b: usize, c: usize, d: usize) -> usize {
        (((a * self.n + b) * self.n + c) * self.n) + d
    }

    fn dfs(&mut self, order: &mut Vec<usize>, used: &mut [bool]) -> bool {
        self.nodes_visited += 1;
        if order.len() > self.max_surviving_prefix.len() {
            self.max_surviving_prefix = order.clone();
        }
        if order.len() == self.n {
            self.survivor_order = Some(order.clone());
            return true;
        }
        if let Some(limit) = self.node_limit {
            if self.nodes_visited >= limit {
                self.stopped_by_limit = true;
                return true;
            }
        }

        for label in 0..self.n {
            if used[label] {
                continue;
            }
            self.stamp = self.stamp.wrapping_add(1);
            if self.stamp == 0 {
                self.local_mark.fill(0);
                self.stamp = 1;
            }
            let mut new_vectors: Vec<usize> = Vec::with_capacity(order.len() * order.len());
            let mut blocked = false;

            for i in 0..order.len() {
                for j in (i + 1)..order.len() {
                    for k in (j + 1)..order.len() {
                        let ids =
                            self.quad_ids[self.quad_index(order[i], order[j], order[k], label)];
                        for vector_id in ids {
                            let inverse = self.inverse_id[vector_id];
                            if let Some(inverse_id) = inverse {
                                if self.counts[inverse_id] > 0
                                    || self.local_mark[inverse_id] == self.stamp
                                {
                                    blocked = true;
                                    break;
                                }
                            }
                            new_vectors.push(vector_id);
                            self.local_mark[vector_id] = self.stamp;
                        }
                        if blocked {
                            break;
                        }
                    }
                    if blocked {
                        break;
                    }
                }
                if blocked {
                    break;
                }
            }

            if blocked {
                self.pruned_branches += 1;
                continue;
            }

            for vector_id in &new_vectors {
                self.counts[*vector_id] += 1;
            }
            used[label] = true;
            order.push(label);
            let done = self.dfs(order, used);
            order.pop();
            used[label] = false;
            for vector_id in &new_vectors {
                self.counts[*vector_id] -= 1;
            }
            if done {
                return true;
            }
        }
        false
    }

    fn add_prefix_label(
        &mut self,
        order: &mut Vec<usize>,
        used: &mut [bool],
        label: usize,
    ) -> bool {
        if label >= self.n || used[label] {
            return false;
        }
        self.stamp = self.stamp.wrapping_add(1);
        if self.stamp == 0 {
            self.local_mark.fill(0);
            self.stamp = 1;
        }
        let mut new_vectors: Vec<usize> = Vec::with_capacity(order.len() * order.len());

        for i in 0..order.len() {
            for j in (i + 1)..order.len() {
                for k in (j + 1)..order.len() {
                    let ids = self.quad_ids[self.quad_index(order[i], order[j], order[k], label)];
                    for vector_id in ids {
                        let inverse = self.inverse_id[vector_id];
                        if let Some(inverse_id) = inverse {
                            if self.counts[inverse_id] > 0
                                || self.local_mark[inverse_id] == self.stamp
                            {
                                return false;
                            }
                        }
                        new_vectors.push(vector_id);
                        self.local_mark[vector_id] = self.stamp;
                    }
                }
            }
        }

        for vector_id in &new_vectors {
            self.counts[*vector_id] += 1;
        }
        used[label] = true;
        order.push(label);
        true
    }
}

fn search_avoiding_order(args: &Args) -> SearchPayload {
    if args.n == 0 {
        fail("n must be positive");
    }
    let started = Instant::now();
    let mut context = SearchContext::new(args.n, &args.offsets, args.node_limit);
    let mut prefix = if args.prefix.is_empty() {
        vec![0]
    } else {
        args.prefix.clone()
    };
    if prefix[0] != 0 {
        fail("--prefix must start with 0; use translation symmetry before calling this tool");
    }
    let mut order = vec![0];
    let mut used = vec![false; args.n];
    used[0] = true;
    let mut prefix_valid = true;
    for label in prefix.iter().skip(1) {
        if !context.add_prefix_label(&mut order, &mut used, *label) {
            prefix_valid = false;
            break;
        }
    }
    if prefix_valid {
        context.dfs(&mut order, &mut used);
    } else {
        context.max_surviving_prefix = order.clone();
    }

    let prefix_is_root = prefix.len() == 1 && prefix[0] == 0;
    let (status, trust) = if !prefix_valid {
        (
            "PREFIX_ALREADY_COMPLETES_TWO_INEQUALITY_KALMANSON_CERTIFICATE",
            "EXACT_PREFIX_OBSTRUCTION_FOR_FIXED_PATTERN",
        )
    } else if context.survivor_order.is_some() {
        (
            "FOUND_ORDER_WITHOUT_TWO_INEQUALITY_KALMANSON_CERTIFICATE",
            "EXACT_COUNTEREXAMPLE_TO_THIS_FILTER_ONLY",
        )
    } else if context.stopped_by_limit {
        ("UNKNOWN_NODE_LIMIT_REACHED", "BOUNDED_SEARCH_DIAGNOSTIC")
    } else if prefix_is_root {
        (
            "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION",
            "EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN",
        )
    } else {
        (
            "EXACT_PREFIX_SUBTREE_TWO_INEQUALITY_KALMANSON_OBSTRUCTION",
            "EXACT_PREFIX_SUBTREE_OBSTRUCTION_FOR_FIXED_PATTERN",
        )
    };

    SearchPayload {
        name: args.name.clone(),
        n: args.n,
        offsets: args.offsets.clone(),
        node_limit: args.node_limit,
        prefix: std::mem::take(&mut prefix),
        prefix_valid,
        nodes_visited: context.nodes_visited,
        pruned_branches: context.pruned_branches,
        max_surviving_prefix: context.max_surviving_prefix,
        survivor_order: context.survivor_order,
        status: status.to_string(),
        trust: trust.to_string(),
        elapsed_seconds: started.elapsed().as_secs_f64(),
    }
}

fn json_usize_list(values: &[usize]) -> String {
    let items: Vec<String> = values.iter().map(|value| value.to_string()).collect();
    format!("[{}]", items.join(", "))
}

fn json_isize_list(values: &[isize]) -> String {
    let items: Vec<String> = values.iter().map(|value| value.to_string()).collect();
    format!("[{}]", items.join(", "))
}

fn print_json(payload: &SearchPayload) {
    println!("{{");
    println!("  \"type\": \"kalmanson_two_inverse_pair_order_search_fast_v1\",");
    println!("  \"trust\": \"{}\",", payload.trust);
    println!("  \"status\": \"{}\",", payload.status);
    println!("  \"pattern\": {{");
    println!(
        "    \"circulant_offsets\": {},",
        json_isize_list(&payload.offsets)
    );
    println!("    \"n\": {},", payload.n);
    println!("    \"name\": \"{}\"", payload.name);
    println!("  }},");
    match payload.node_limit {
        Some(limit) => println!("  \"node_limit\": {},", limit),
        None => println!("  \"node_limit\": null,"),
    }
    println!("  \"prefix\": {},", json_usize_list(&payload.prefix));
    println!("  \"prefix_valid\": {},", payload.prefix_valid);
    println!("  \"nodes_visited\": {},", payload.nodes_visited);
    println!(
        "  \"branches_pruned_by_completed_two_certificate\": {},",
        payload.pruned_branches
    );
    println!(
        "  \"max_surviving_prefix_depth\": {},",
        payload.max_surviving_prefix.len()
    );
    println!(
        "  \"max_surviving_prefix\": {},",
        json_usize_list(&payload.max_surviving_prefix)
    );
    match &payload.survivor_order {
        Some(order) => println!("  \"survivor_order\": {},", json_usize_list(order)),
        None => println!("  \"survivor_order\": null,"),
    }
    println!("  \"elapsed_seconds\": {:.6}", payload.elapsed_seconds);
    println!("}}");
}

fn assert_c13_expected(payload: &SearchPayload) {
    if payload.name != "C13_sidon_1_2_4_10" {
        fail("unexpected pattern for --assert-c13-expected");
    }
    if payload.status != "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION" {
        fail(&format!("unexpected status: {}", payload.status));
    }
    if payload.nodes_visited != 1_496_677 {
        fail(&format!("unexpected node count: {}", payload.nodes_visited));
    }
    if payload.pruned_branches != 6_192_576 {
        fail(&format!(
            "unexpected prune count: {}",
            payload.pruned_branches
        ));
    }
    if payload.max_surviving_prefix.len() != 11 {
        fail(&format!(
            "unexpected max prefix depth: {}",
            payload.max_surviving_prefix.len()
        ));
    }
    if payload.survivor_order.is_some() {
        fail("unexpected survivor order");
    }
}

fn main() {
    let args = parse_args();
    let payload = search_avoiding_order(&args);

    if args.assert_obstructed
        && payload.status != "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION"
    {
        fail(&format!(
            "search did not prove all-order obstruction: {}",
            payload.status
        ));
    }
    if args.assert_c13_expected {
        assert_c13_expected(&payload);
    }

    if args.json {
        print_json(&payload);
    } else {
        println!(
            "{} {} nodes={} pruned={} max_prefix={} elapsed={:.3}s",
            payload.name,
            payload.status,
            payload.nodes_visited,
            payload.pruned_branches,
            payload.max_surviving_prefix.len(),
            payload.elapsed_seconds
        );
    }
}
