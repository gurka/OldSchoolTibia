#include <cstring>
#include "rsa.h"

RSA::RSA()
{
  mpz_init(n_);
  mpz_init2(d_, 1024);
}

RSA::~RSA()
{
  mpz_clear(n_);
  mpz_clear(d_);
}

void RSA::setPrivateKey(const char* p_str, const char* q_str)
{
  mpz_t p;
  mpz_t q;
  mpz_t e;

  mpz_init2(p, 1024);
  mpz_init2(q, 1024);
  mpz_init(e);

  mpz_set_str(p, p_str, 10);
  mpz_set_str(q, q_str, 10);

  // e = 65537
  mpz_set_ui(e, 65537);

  // n = p * q
  mpz_mul(n_, p, q);

  // d = e^-1 mod (p - 1)(q - 1)
  mpz_t p_1;
  mpz_t q_1;
  mpz_t pq_1;
  mpz_init2(p_1, 1024);
  mpz_init2(q_1, 1024);
  mpz_init2(pq_1, 1024);

  mpz_sub_ui(p_1, p, 1);
  mpz_sub_ui(q_1, q, 1);

  // pq_1 = (p - 1)(q - 1)
  mpz_mul(pq_1, p_1, q_1);

  // d = e^-1 mod (p - 1)(q - 1)
  mpz_invert(d_, e, pq_1);

  mpz_clear(p_1);
  mpz_clear(q_1);
  mpz_clear(pq_1);

  mpz_clear(p);
  mpz_clear(q);
  mpz_clear(e);
}

void RSA::decrypt(char* msg)
{
  mpz_t c;
  mpz_t m;

  mpz_init2(c, 1024);
  mpz_init2(m, 1024);

  mpz_import(c, 128, 1, 1, 0, 0, msg);

  mpz_powm(m, c, d_, n_);

  size_t count = (mpz_sizeinbase(m, 2) + 7) / 8;

  memset(msg, 0, 128 - count);
  size_t dummy;
  mpz_export(&msg[128 - count], &dummy, 1, 1, 0, 0, m);

  mpz_clear(c);
  mpz_clear(m);
}
